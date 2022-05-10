import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import redis
from deepdiff import DeepDiff

from tracardi.config import tracardi, memory_cache
from tracardi.domain.entity import Entity

from tracardi.service.console_log import ConsoleLog
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.destination_manager import DestinationManager
from tracardi.service.merging import merge
from tracardi.service.notation.dot_accessor import DotAccessor

from tracardi.domain.event_payload_validator import EventPayloadValidator
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.domain.console import Console
from tracardi.exceptions.exception_service import get_traceback
from tracardi.service.event_validator import validate
from tracardi.domain.event import Event, VALIDATED, ERROR, WARNING, PROCESSED, INVALID
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.value_object.tracker_payload_result import TrackerPayloadResult
from tracardi.exceptions.exception import UnauthorizedException, StorageException, FieldTypeConflictException, \
    EventValidationException, TracardiException
from tracardi.process_engine.rules_engine import RulesEngine
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.segmentation import segment
from tracardi.service.storage.driver import storage
from tracardi.service.storage.factory import StorageForBulk
from tracardi.service.storage.helpers.source_cacher import source_cache
from tracardi.service.synchronizer import ProfileTracksSynchronizer

logger = logging.getLogger('app.api.track.service.tracker')
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = MemoryCache()


async def _persist(profile_less, console_log: ConsoleLog, session: Session, events: List[Event],
                   tracker_payload: TrackerPayload, profile: Optional[Profile] = None) -> CollectResult:
    # Save profile
    try:
        if isinstance(profile, Profile) and profile.operation.new:
            save_profile_result = await storage.driver.profile.save_profile(profile)
        else:
            save_profile_result = BulkInsertResult()
    except StorageException as e:
        raise FieldTypeConflictException("Could not save profile. Error: {}".format(e.message), rows=e.details)

    # Save session
    try:
        persist_session = tracker_payload.is_on('saveSession', default=True)
        save_session_result = await storage.driver.session.save_session(session, profile, profile_less, persist_session)
    except StorageException as e:
        raise FieldTypeConflictException("Could not save session. Error: {}".format(e.message), rows=e.details)

    # Save events
    try:
        persist_events = tracker_payload.is_on('saveEvents', default=True)

        # Set statuses
        log_event_journal = console_log.get_indexed_event_journal()
        debugged = tracker_payload.is_debugging_on()

        for event in events:

            event.metadata.time.process_time = datetime.timestamp(datetime.utcnow()) - datetime.timestamp(
                event.metadata.time.insert)

            # Reset session id if session is not saved
            if tracker_payload.is_on('saveSession', default=True) is False:
                event.session = None

            if event.id in log_event_journal:
                log = log_event_journal[event.id]
                if log.is_error():
                    event.metadata.status = ERROR
                    continue
                elif log.is_warning():
                    event.metadata.status = WARNING
                    continue
                else:
                    event.metadata.status = PROCESSED

        save_events_result = await storage.driver.event.save_events(events, persist_events)

    except StorageException as e:
        raise FieldTypeConflictException("Could not save event. Error: {}".format(e.message), rows=e.details)

    return CollectResult(
        session=save_session_result,
        profile=save_profile_result,
        events=save_events_result
    )


async def validate_events_json_schemas(events, profile: Optional[Profile], session, console_log: ConsoleLog):
    for event in events:
        dot = DotAccessor(
            profile=profile,
            session=session,
            payload=None,
            event=event,
            flow=None
        )
        event_type = dot.event['type']

        if event_type not in cache:
            logger.info(f"Refreshed validation schema for event type {event_type}.")
            event_payload_validator = await storage.driver.validation_schema.load_schema(
                dot.event['type'])  # type: EventPayloadValidator
            cache[event_type] = CacheItem(data=event_payload_validator, ttl=memory_cache.event_validator_ttl)

        validation_data = cache[event_type].data

        if validation_data is not None:
            try:
                validate(dot, validator=validation_data)
                event.metadata.status = VALIDATED
            except EventValidationException as e:
                event.metadata.status = INVALID
                console_log.append(
                    Console(
                        profile_id=profile.id if isinstance(profile, Entity) else None,
                        origin='profile',
                        class_name='EventValidator',
                        module='tracker',
                        type='error',
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

    if profile_less is True and profile is not None:
        logger.warning("Something is wrong - profile less events should not have profile attached.")

    if has_profile:
        profile_copy = profile.dict(exclude={"operation": ...})

    # Get events
    events = tracker_payload.get_events(session, profile, profile_less, ip)

    # Validates json schemas of events, throws exception if data is not valid
    console_log = await validate_events_json_schemas(events, profile, session, console_log)

    debugger = None
    segmentation_result = None

    rules_engine = RulesEngine(
        session,
        profile,
        events_rules=storage.driver.rule.load_rules(tracker_payload.source, events),
        console_log=console_log
    )

    ux = []
    post_invoke_events = None
    try:

        # Invoke rules engine
        debugger, ran_event_types, console_log, post_invoke_events, invoked_rules = await rules_engine.invoke(
            storage.driver.flow.load_production_flow,
            ux,
            tracker_payload.source.id
        )

        # append invoked rules to event metadata

        for event in events:
            if event.type in invoked_rules:
                event.metadata.processed_by.rules = invoked_rules[event.type]

        # Profile less events can not be segmented as there is no profile to segment
        # todo wf can return profile so the above may not be true

        if profile_less is False:
            # Segment
            segmentation_result = await segment(rules_engine.profile,
                                                ran_event_types,
                                                storage.driver.segment.load_segments)

    except Exception as e:
        message = 'Rules engine or segmentation returned an error `{}`'.format(str(e))
        console_log.append(
            Console(
                profile_id=rules_engine.profile.id if isinstance(rules_engine.profile, Entity) else None,
                origin='profile',
                class_name='RulesEngine',
                module='tracker',
                type='error',
                message=message,
                traceback=get_traceback(e)
            )
        )
        logger.error(message)

    save_tasks = []
    try:
        # Merge
        profiles_to_disable = await merge(rules_engine.profile, limit=2000)
        if profiles_to_disable is not None:
            task = asyncio.create_task(
                StorageForBulk(profiles_to_disable).index('profile').save())
            save_tasks.append(task)
    except Exception as e:
        message = 'Profile merging returned an error `{}`'.format(str(e))
        logger.error(message)
        console_log.append(
            Console(
                profile_id=rules_engine.profile.id if isinstance(rules_engine.profile, Entity) else None,
                origin='profile',
                class_name='merge',
                module='app.api.track.service',
                type='error',
                message=message,
                traceback=get_traceback(e)
            )
        )

    # Must be the last operation
    try:
        if isinstance(rules_engine.profile, Profile) and rules_engine.profile.operation.needs_update():
            await storage.driver.profile.save_profile(profile)
    except Exception as e:
        message = "Profile update returned an error: `{}`".format(str(e))
        console_log.append(
            Console(
                profile_id=rules_engine.profile.id if isinstance(rules_engine.profile, Entity) else None,
                origin='profile',
                class_name='tracker',
                module='tracker',
                type='error',
                message=message,
                traceback=get_traceback(e)
            )
        )
        logger.error(message)

    # Send to destination

    if has_profile and profile_copy is not None:
        profile_delta = DeepDiff(profile_copy, profile.dict(exclude={"operation": ...}), ignore_order=True)
        if profile_delta:
            logger.info("Profile changed. Destination scheduled to run.")
            try:
                destination_manager = DestinationManager(profile_delta,
                                                         profile,
                                                         session,
                                                         payload=None,
                                                         event=None,
                                                         flow=None)
                await destination_manager.send_data(profile.id, debug=False)
            except Exception as e:
                # todo - this appends error to the same profile - it rather should be en event error
                console_log.append(Console(
                    profile_id=rules_engine.profile.id if isinstance(rules_engine.profile, Entity) else None,
                    origin='destination',
                    class_name='DestinationManager',
                    module='tracker',
                    type='error',
                    message=str(e),
                    traceback=get_traceback(e)
                ))
                logger.error(str(e))

    try:
        if tracardi.track_debug or tracker_payload.is_on('debugger', default=False):
            if debugger.has_call_debug_trace():
                # Save debug info
                save_tasks.append(
                    asyncio.create_task(
                        storage.driver.debug_info.save_debug_info(
                            debugger
                        )
                    )
                )

            # Run tasks
            await asyncio.gather(*save_tasks)

    except Exception as e:
        message = "Error during saving debug info: `{}`".format(str(e))
        logger.error(message)
        console_log.append(
            Console(
                profile_id=rules_engine.profile.id if isinstance(rules_engine.profile, Entity) else None,
                origin='profile',
                class_name='tracker',
                module='tracker',
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

        collect_result = await _persist(profile_less, console_log, session, events, tracker_payload, profile)

        # Save console log
        if console_log:
            encoded_console_log = list(console_log.get_encoded())
            save_tasks.append(asyncio.create_task(StorageForBulk(encoded_console_log).index('console-log').save()))

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

    return result


async def track_event(tracker_payload: TrackerPayload, ip: str, profile_less: bool):

    try:
        source = await source_cache.validate_source(source_id=tracker_payload.source.id)
    except ValueError as e:
        raise UnauthorizedException(e)

    if source.transitional is True:
        tracker_payload.options.update({
            "saveSession": False,
            "saveEvents": False
        })

    if source.returns_profile is False:
        tracker_payload.options.update({
            "profile": False
        })

    # Get session
    if tracker_payload.session.id is None:
        raise UnauthorizedException("Session must be set.")

    # Load session from storage
    session = await storage.driver.session.load(tracker_payload.session.id)  # type: Session

    # Get profile
    profile, session = await tracker_payload.get_profile_and_session(session,
                                                                     storage.driver.profile.load_merged_profile,
                                                                     profile_less
                                                                     )

    return await invoke_track_process(tracker_payload, source, profile_less, profile, session, ip)


async def synchronized_event_tracking(tracker_payload: TrackerPayload, host: str, profile_less: bool):
    if tracardi.sync_profile_tracks:
        try:
            async with ProfileTracksSynchronizer(tracker_payload.profile, wait=1):
                return await track_event(tracker_payload, ip=host, profile_less=profile_less)
        except redis.exceptions.ConnectionError as e:
            raise TracardiException(f"Could not connect to Redis server. Connection returned error {str(e)}")
    else:
        return await track_event(tracker_payload, ip=host, profile_less=profile_less)
