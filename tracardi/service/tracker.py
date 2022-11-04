import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import redis
from deepdiff import DeepDiff

from tracardi.config import tracardi
from tracardi.domain.entity import Entity
from tracardi.domain.value_object.operation import Operation
from tracardi.process_engine.debugger import Debugger

from tracardi.service.console_log import ConsoleLog
from tracardi.event_server.utils.memory_cache import MemoryCache
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.destination_manager import DestinationManager
from tracardi.service.merging import merge
from tracardi.service.notation.dot_accessor import DotAccessor

from tracardi.domain.event_payload_validator import EventTypeManager
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.domain.console import Console
from tracardi.exceptions.exception_service import get_traceback
from tracardi.service.event_validator import validate
from tracardi.domain.event import Event, PROCESSED
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata, SessionTime
from tracardi.domain.value_object.tracker_payload_result import TrackerPayloadResult
from tracardi.exceptions.exception import UnauthorizedException, StorageException, FieldTypeConflictException, \
    TracardiException, DuplicatedRecordException
from tracardi.process_engine.rules_engine import RulesEngine
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.segmentation import segment
from tracardi.service.consistency.session_corrector import correct_session
from tracardi.service.storage.driver import storage
from tracardi.service.storage.helpers.source_cacher import source_cache
from tracardi.service.synchronizer import ProfileTracksSynchronizer
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses
from tracardi.service.event_props_reshaper import EventPropsReshaper, EventPropsReshapingError
from tracardi.service.event_manager_cache import EventManagerCache

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = MemoryCache()
event_manager_cache = EventManagerCache()


async def _save_profile(profile):
    try:
        if isinstance(profile, Profile) and (profile.operation.new or profile.operation.needs_update()):
            return await storage.driver.profile.save(profile)
        else:
            return BulkInsertResult()

    except StorageException as e:
        raise FieldTypeConflictException("Could not save profile. Error: {}".format(str(e)), rows=e.details)


async def _save_session(tracker_payload, session, profile):
    try:
        persist_session = tracker_payload.is_on('saveSession', default=True)
        result = await storage.driver.session.save_session(session, profile, persist_session)
        if session.operation.new:
            """
            Until the session is saved and it is usually within 1s the system can create many profiles for 1 session. 
            System checks if the session exists by loading it from ES. If it is a new session then is does not exist 
            and must be saved before it can be read. So there is a 1s when system thinks that the session does not 
            exist.

            If session is new we will refresh the session in ES.
            """

            await storage.driver.session.refresh()
        return result
    except StorageException as e:
        raise FieldTypeConflictException("Could not save session. Error: {}".format(str(e)), rows=e.details)


async def _save_events(tracker_payload, console_log, events):
    try:
        persist_events = tracker_payload.is_on('saveEvents', default=True)

        # Set statuses
        log_event_journal = console_log.get_indexed_event_journal()

        for event in events:

            event.metadata.time.process_time = datetime.timestamp(datetime.utcnow()) - datetime.timestamp(
                event.metadata.time.insert)

            # Reset session id if session is not saved

            if tracker_payload.is_on('saveSession', default=True) is False:
                # DO NOT remove session if it already exists in db
                if not isinstance(event.session, Entity) or not await storage.driver.session.exist(event.session.id):
                    event.session = None

            if event.id in log_event_journal:
                log = log_event_journal[event.id]
                if log.is_error():
                    event.metadata.error = True
                    continue
                elif log.is_warning():
                    event.metadata.warning = True
                    continue
                else:
                    event.metadata.status = PROCESSED

        return await storage.driver.event.save_events(events, persist_events)

    except StorageException as e:
        raise FieldTypeConflictException("Could not save event. Error: {}".format(str(e)), rows=e.details)


async def _persist(console_log: ConsoleLog, session: Session, events: List[Event],
                   tracker_payload: TrackerPayload, profile: Optional[Profile] = None) -> CollectResult:

    results = await asyncio.gather(
        _save_profile(profile),
        _save_session(tracker_payload, session, profile),
        _save_events(tracker_payload, console_log, events)
    )

    return CollectResult(
        profile=results[0],
        session=results[1],
        events=results[2]
    )


async def validate_and_reshape_events(events, profile: Optional[Profile], session, console_log: ConsoleLog):

    # There may be many event is tracker_payload

    for index, event in enumerate(events):
        dot = DotAccessor(
            profile=profile,
            session=session,
            payload=None,
            event=event,
            flow=None,
            memory=None
        )

        event_type = dot.event['type']
        event_type_manager = event_manager_cache.get_item(event_type)

        if event_type_manager is None:
            event_type_manager = await storage.driver.event_management.load_event_type_metadata(
                dot.event['type'])  # type: EventTypeManager
            if event_type_manager is not None:
                event_manager_cache.upsert_item(event_type_manager)

        if event_type_manager is not None:
            try:
                if event_type_manager.validation.enabled is True:
                    if validate(dot, validator=event_type_manager) is False:
                        event.metadata.valid = False
                        console_log.append(
                            Console(
                                flow_id=None,
                                node_id=None,
                                event_id=event.id,
                                profile_id=get_entity_id(profile),
                                origin='profile',
                                class_name='EventValidator',
                                module=__name__,
                                type='error',
                                message="Event is invalid."
                            )
                        )
                if event.metadata.valid:
                    events[index] = EventPropsReshaper(dot=dot, event=event).reshape(
                        schema=event_type_manager.reshaping
                    )

            except EventPropsReshapingError as e:
                console_log.append(
                    Console(
                        event_id=event.id,
                        profile_id=get_entity_id(profile),
                        origin='profile',
                        class_name='EventPropsReshaping',
                        module=__name__,
                        type='warning',
                        message=str(e),
                        traceback=get_traceback(e)
                    )
                )

    return console_log


async def invoke_track_process(tracker_payload: TrackerPayload, source, profile_less: bool, profile=None, session=None,
                               ip='0.0.0.0'):
    console_log = ConsoleLog()
    profile_copy = None

    has_profile = not profile_less and isinstance(profile, Profile)

    # Calculate last visit
    if has_profile:
        # Calculate only on first click in visit
        if session.operation.new:
            logger.info("Profile visits metadata changed.")
            profile.metadata.time.visit.set_visits_times()
            profile.metadata.time.visit.count += 1
            profile.operation.update = True
            # Set time zone form session
            if session.context:
                try:
                    profile.metadata.time.visit.tz = session.context['time']['tz']
                except KeyError:
                    pass

    if profile_less is True and profile is not None:
        logger.warning("Something is wrong - profile less events should not have profile attached.")

    if has_profile:
        profile_copy = profile.dict(exclude={"operation": ...})

    # Get events
    events = tracker_payload.get_events(session, profile, has_profile, ip)

    # Validates json schemas of events and reshapes properties
    # todo bad design - events gets mutated
    console_log = await validate_and_reshape_events(events, profile, session, console_log)

    debugger = None
    segmentation_result = None

    # Skips INVALID events in invoke method
    rules_engine = RulesEngine(
        session,
        profile,
        events_rules=await storage.driver.rule.load_rules(tracker_payload.source, events),
        console_log=console_log
    )

    ux = []

    # if source.requires_consent is True:
    #     ux.append({
    #
    #     })

    post_invoke_events = None
    flow_responses = FlowResponses([])
    try:

        # Invoke rules engine
        rule_invoke_result = await rules_engine.invoke(
            storage.driver.flow.load_production_flow,
            ux,
            tracker_payload
        )

        debugger = rule_invoke_result.debugger
        ran_event_types = rule_invoke_result.ran_event_types
        console_log = rule_invoke_result.console_log
        post_invoke_events = rule_invoke_result.post_invoke_events
        invoked_rules = rule_invoke_result.invoked_rules
        flow_responses = FlowResponses(rule_invoke_result.flow_responses)

        # Profile and session can change inside workflow
        # Check if it should not be replaced.

        if profile is not rules_engine.profile:
            profile = rules_engine.profile

        if session is not rules_engine.session:
            session = rules_engine.session

        # Append invoked rules to event metadata

        for event in events:
            if event.type in invoked_rules:
                event.metadata.processed_by.rules = invoked_rules[event.type]

        # Segment only if there is profile

        if isinstance(profile, Profile):
            # Segment
            segmentation_result = await segment(profile,
                                                ran_event_types,
                                                storage.driver.segment.load_segments)

    except Exception as e:
        message = 'Rules engine or segmentation returned an error `{}`'.format(str(e))
        console_log.append(
            Console(
                flow_id=None,
                node_id=None,
                event_id=None,
                profile_id=get_entity_id(profile),
                origin='profile',
                class_name='invoke_track_process',
                module=__name__,
                type='error',
                message=message,
                traceback=get_traceback(e)
            )
        )
        logger.error(message)

    save_tasks = []
    try:
        # Merge
        profiles_to_disable = await merge(profile, override_old_data=True, limit=2000)
        if profiles_to_disable is not None:
            task = asyncio.create_task(
                storage.driver.profile.save_all(profiles_to_disable)
            )
            save_tasks.append(task)
    except Exception as e:
        message = 'Profile merging returned an error `{}`'.format(str(e))
        logger.error(message)
        console_log.append(
            Console(
                flow_id=None,
                node_id=None,
                event_id=None,
                profile_id=get_entity_id(profile),
                origin='profile',
                class_name='invoke_track_process',
                module=__name__,
                type='error',
                message=message,
                traceback=get_traceback(e)
            )
        )

    try:
        if tracardi.track_debug or tracker_payload.is_on('debugger', default=False):
            if isinstance(debugger, Debugger) and debugger.has_call_debug_trace():
                # Save debug info
                save_tasks.append(
                    asyncio.create_task(
                        storage.driver.debug_info.save_debug_info(
                            debugger
                        )
                    )
                )

    except Exception as e:
        message = "Error during saving debug info: `{}`".format(str(e))
        logger.error(message)
        console_log.append(
            Console(
                flow_id=None,
                node_id=None,
                event_id=None,
                profile_id=get_entity_id(profile),
                origin='profile',
                class_name='invoke_track_process',
                module=__name__,
                type='error',
                message=message,
                traceback=get_traceback(e)
            )
        )

    finally:
        # todo maybe persisting profile is not necessary - it is persisted right after workflow - see above
        # TODO notice that profile is saved only when it's new change it when it need update
        # Save profile, session, events

        # Synchronize post invoke events. Replace events with events changed by WF.
        # Events are saved only if marked in event.update==true
        if post_invoke_events is not None:
            synced_events = []
            for ev in events:
                if ev.update is True and ev.id in post_invoke_events:
                    synced_events.append(post_invoke_events[ev.id])
                else:
                    synced_events.append(ev)

            events = synced_events

        collect_result = await _persist(console_log, session, events, tracker_payload, profile)

        # Save console log
        if console_log:
            encoded_console_log = list(console_log.get_encoded())
            save_tasks.append(asyncio.create_task(storage.driver.console_log.save_all(encoded_console_log)))

    # Send to destination

    if has_profile and profile_copy is not None:
        new_profile = profile.dict(exclude={"operation": ...})

        if profile_copy != new_profile:
            profile_delta = DeepDiff(profile_copy, new_profile, ignore_order=True)
            if profile_delta:
                logger.info("Profile changed. Destination scheduled to run.")
                try:
                    destination_manager = DestinationManager(profile_delta,
                                                             profile,
                                                             session,
                                                             payload=None,
                                                             event=None,
                                                             flow=None,
                                                             memory=None)
                    # todo performance - could be not awaited add to save_task
                    await destination_manager.send_data(profile.id, events, debug=False)
                except Exception as e:
                    # todo - this appends error to the same profile - it rather should be en event error
                    console_log.append(Console(
                        flow_id=None,
                        node_id=None,
                        event_id=None,
                        profile_id=get_entity_id(profile),
                        origin='destination',
                        class_name='DestinationManager',
                        module=__name__,
                        type='error',
                        message=str(e),
                        traceback=get_traceback(e)
                    ))
                    logger.error(str(e))

    if save_tasks:
        # Run tasks
        await asyncio.gather(*save_tasks)

    # Prepare response
    result = {}

    # Debugging
    # todo save result to different index
    if tracker_payload.is_debugging_on():
        debug_result = TrackerPayloadResult(**collect_result.dict())
        debug_result = debug_result.dict()
        debug_result['execution'] = debugger
        debug_result['segmentation'] = segmentation_result
        debug_result['logs'] = console_log
        result['debugging'] = debug_result

    # Add profile to response
    if tracker_payload.return_profile() and profile_less is True:
        logger.warning("It does not make sense to return profile on profile less event. There is no profile to return.")

    if profile_less is False:
        if tracker_payload.return_profile():
            result["profile"] = profile.dict(
                exclude={
                    "traits": {"private": ...},
                    "pii": ...,
                    "operation": ...
                })
        else:
            result["profile"] = profile.dict(include={"id": ...})

    # Add source to response
    result['source'] = source.dict(include={"consent": ...})

    # Add UX to response
    result['ux'] = ux

    result['response'] = flow_responses.merge()

    return result


async def track_event(tracker_payload: TrackerPayload, ip: str, profile_less: bool, allowed_bridges: List[str],
                      internal_source=None):
    try:
        if internal_source is not None:
            if internal_source.id != tracker_payload.source.id:
                raise ValueError(f"Invalid event source `{tracker_payload.source.id}`")
            source = internal_source
        else:
            source = await source_cache.validate_source(source_id=tracker_payload.source.id,
                                                        allowed_bridges=allowed_bridges)
    except ValueError as e:
        raise UnauthorizedException(e)

    tracker_payload.set_transitional(source)
    tracker_payload.set_return_profile(source)
    tracker_payload.force_there_is_a_session()

    # Load session from storage
    try:
        session = await storage.driver.session.load_by_id(tracker_payload.session.id)  # type: Optional[Session]

    except DuplicatedRecordException as e:

        # There may be a case when we have 2 sessions with the same id.
        logger.error(str(e))

        # Try to recover sessions
        list_of_profile_ids_referenced_by_session = await correct_session(tracker_payload.session.id)

        # If there is duplicated session create new random session. As a consequence of this a new profile is created.
        session = Session(
            id=tracker_payload.session.id,
            metadata=SessionMetadata(
                time=SessionTime(
                    insert=datetime.utcnow()
                )
            ),
            operation=Operation(
                new=True
            )
        )

        # If duplicated sessions referenced the same profile then keep it.
        if len(list_of_profile_ids_referenced_by_session) == 1:
            session.profile = Entity(id=list_of_profile_ids_referenced_by_session[0])

    # Get profile
    profile, session = await tracker_payload.get_profile_and_session(
        session,
        storage.driver.profile.load_merged_profile,
        profile_less
    )
    return await invoke_track_process(tracker_payload, source, profile_less, profile, session, ip)


async def synchronized_event_tracking(tracker_payload: TrackerPayload, host: str, profile_less: bool,
                                      allowed_bridges: List[str], internal_source=None):
    if tracardi.sync_profile_tracks:
        try:
            async with ProfileTracksSynchronizer(tracker_payload.profile, wait=tracardi.sync_profile_tracks_wait,
                                                 max_repeats=tracardi.sync_profile_tracks_max_repeats):
                return await track_event(tracker_payload, ip=host, profile_less=profile_less,
                                         allowed_bridges=allowed_bridges, internal_source=internal_source)
        except redis.exceptions.ConnectionError as e:
            raise TracardiException(f"Could not connect to Redis server. Connection returned error {str(e)}")
    else:
        return await track_event(tracker_payload, ip=host, profile_less=profile_less, allowed_bridges=allowed_bridges,
                                 internal_source=internal_source)
