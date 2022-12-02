import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pprint import pprint
from typing import List, Optional, Tuple, Dict, Callable, Union
from uuid import uuid4

import redis
from deepdiff import DeepDiff

from tracardi.config import tracardi, memory_cache
from tracardi.domain.entity import Entity
from tracardi.domain.event_source import EventSource
from tracardi.domain.value_object.operation import Operation
from tracardi.process_engine.debugger import Debugger
from tracardi.service.cache_manager import CacheManager

from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.destination_manager import DestinationManager
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.console import Console
from tracardi.exceptions.exception_service import get_traceback
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata, SessionTime
from tracardi.domain.value_object.tracker_payload_result import TrackerPayloadResult
from tracardi.exceptions.exception import UnauthorizedException, \
    TracardiException, DuplicatedRecordException
from tracardi.process_engine.rules_engine import RulesEngine
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.pool_manager import PoolManager
from tracardi.service.profile_merger import ProfileMerger
from tracardi.service.segmentation import segment
from tracardi.service.consistency.session_corrector import correct_session
from tracardi.service.storage.driver import storage
from tracardi.service.storage.helpers.source_cacher import validate_source
from tracardi.service.synchronizer import ProfileTracksSynchronizer
from tracardi.service.tracker_event_reshaper import reshape_event
from tracardi.service.tracker_event_validator import validate_event
from tracardi.service.tracker_persister import persist
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_response import FlowResponses

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


@dataclass
class TrackerResult:
    tracker_payload: TrackerPayload
    response: dict
    events: List[Event]
    session: Optional[Session] = None
    profile: Optional[Profile] = None
    console_log: Optional[ConsoleLog] = None


async def save_data(console_log: ConsoleLog, session: Session, events: List[Event],
                    tracker_payload: TrackerPayload, profile: Optional[Profile] = None):
    pprint(events)
    pprint(session)
    pprint(profile)
    await persist(
        console_log,
        session,
        events,
        tracker_payload,
        profile)


async def send_data(grouped_tracker_payloads: Dict[str, List[TrackerPayload]], attributes):
    source, ip, run_async, static_profile_id = attributes
    print("grouped", len(grouped_tracker_payloads['8053d658529deac0522bc903a2d398e36f3d19f5']))

    for finger_print, tracker_payloads in grouped_tracker_payloads.items():
        print("invoke", len(tracker_payloads))
        await _invoke_track_process_step_0(
            tracker_payloads,
            source,
            ip,
            run_async,
            static_profile_id
        )


pool = PoolManager('event-pooling',
                   max_pool=10,
                   pass_pool_as_dict=True,
                   on_pool_purge=send_data)


async def validate_and_reshape_events(events, profile: Optional[Profile], session, console_log: ConsoleLog) -> Tuple[
    List[Event], ConsoleLog]:
    dot = DotAccessor(
        profile=profile,
        session=session,
        payload=None,
        event=None,
        flow=None,
        memory=None
    )

    processed_events = []
    for event in events:

        dot.set_storage("event", event)

        # mutates console_log
        event = await validate_event(event, dot, console_log)

        try:
            event = await reshape_event(event, dot)
        except Exception as e:
            console_log.append(
                Console(
                    event_id=event.id,
                    profile_id=get_entity_id(profile),
                    origin='tracker',
                    class_name='tracker',
                    module=__name__,
                    type='error',
                    message=str(e),
                    traceback=get_traceback(e)
                )
            )

        processed_events.append(event)

    return processed_events, console_log


async def invoke_track_process_step_2(tracker_payload: TrackerPayload,
                                      source: EventSource,
                                      profile_less: bool,
                                      persister: Callable,
                                      profile=None,
                                      session=None,
                                      ip='0.0.0.0'
                                      ) -> TrackerResult:

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
    events, console_log = await validate_and_reshape_events(events, profile, session, console_log)

    debugger = None
    segmentation_result = None

    # Routing rules are subject to caching
    event_rules = await storage.driver.rule.load_rules(tracker_payload.source, events)

    ux = []
    post_invoke_events = None
    flow_responses = FlowResponses([])

    #  If no event_rules for delivered event then no need to run rule invoke
    #  and no need for profile merging
    if event_rules is not None:

        # Skips INVALID events in invoke method
        rules_engine = RulesEngine(
            session,
            profile,
            events_rules=event_rules,
            console_log=console_log
        )

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
                    class_name='invoke_track_process_step_2',
                    module=__name__,
                    type='error',
                    message=message,
                    traceback=get_traceback(e)
                )
            )
            logger.error(message)

        # Profile merge
        try:
            if profile is not None:  # Profile can be None if profile_less event is processed
                if profile.operation.needs_merging():
                    merge_key_values = ProfileMerger.get_merging_keys_and_values(profile)
                    merged_profile = await ProfileMerger.invoke_merge_profile(
                        profile,
                        merge_by=merge_key_values,
                        override_old_data=True,
                        limit=1000)

                    if merged_profile is not None:
                        # Replace profile with merged_profile
                        profile = merged_profile

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
                    class_name='invoke_track_process_step_2',
                    module=__name__,
                    type='error',
                    message=message,
                    traceback=get_traceback(e)
                )
            )

    save_tasks = []
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
                class_name='invoke_track_process_step_2',
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

        track_result = TrackerResult(
            session=session,
            profile=profile,
            events=events,
            tracker_payload=tracker_payload,
            console_log=console_log
        )
        # collect_result = await persister(console_log, session, events, tracker_payload, profile)
        # save_tasks.append(asyncio.create_task(_persist(console_log, session, events, tracker_payload, profile)))

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
                    # todo performance - could be not awaited  - add to save_task
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

    # # Debugging
    # # todo save result to different index
    # if tracker_payload.is_debugging_on():
    #     debug_result = TrackerPayloadResult(**collect_result.dict())
    #     debug_result = debug_result.dict()
    #     debug_result['execution'] = debugger
    #     debug_result['segmentation'] = segmentation_result
    #     debug_result['logs'] = console_log
    #     result['debugging'] = debug_result

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

    # todo track_result may not exist
    track_result.response = result

    return track_result


async def track_event(tracker_payload: TrackerPayload,
                      ip: str,
                      allowed_bridges: List[str],
                      internal_source=None,
                      run_async: bool = False,
                      static_profile_id: bool = False
                      ):

    # Trim ids - spaces are frequent issues

    if tracker_payload.source:
        tracker_payload.source.id = tracker_payload.source.id.strip()
    if tracker_payload.session:
        tracker_payload.session.id = tracker_payload.session.id.strip()
    if tracker_payload.profile:
        tracker_payload.profile.id = tracker_payload.profile.id.strip()

    # Validate event source

    try:
        if internal_source is not None:
            if internal_source.id != tracker_payload.source.id:
                raise ValueError(f"Invalid event source `{tracker_payload.source.id}`")
            source = internal_source
        else:
            source = await validate_source(source_id=tracker_payload.source.id,
                                           allowed_bridges=allowed_bridges)
    except ValueError as e:
        raise UnauthorizedException(e)

    # Async
    pool.set_ttl(asyncio.get_running_loop(), ttl=3)
    pool.set_attributes(
        (source, ip, run_async, static_profile_id)
    )

    # If async
    await pool.append(tracker_payload, key=tracker_payload.get_finger_print())

    # No async

    # Todo no return right now

    # tracker_result = await invoke_track_process_step_0(
    #     [tracker_payload],
    #     source,
    #     ip,
    #     run_async,
    #     static_profile_id
    # )


async def _invoke_track_process_step_0(tracker_payloads: List[TrackerPayload],
                                       source: EventSource,
                                       ip: str,
                                       run_async: bool = False,
                                       static_profile_id: bool = False) -> Union[TrackerResult, List[TrackerResult]]:

    tracker_results = []
    for tracker_payload in tracker_payloads:
        result = await invoke_track_process_step_0(tracker_payload,
                                                   source,
                                                   ip,
                                                   run_async,
                                                   static_profile_id)
        tracker_results.append(result)

    # TODO Save bulk

    return tracker_results


async def invoke_track_process_step_0(tracker_payload: TrackerPayload,
                                      source: EventSource,
                                      ip: str,
                                      run_async: bool = False,
                                      static_profile_id: bool = False) -> TrackerResult:
    try:

        if source.synchronize_profiles:
            async with ProfileTracksSynchronizer(tracker_payload.profile,
                                                 wait=tracardi.sync_profile_tracks_wait,
                                                 max_repeats=tracardi.sync_profile_tracks_max_repeats):
                return await invoke_track_process_step_1(
                    tracker_payload,
                    source,
                    ip=ip,
                    profile_less=tracker_payload.profile_less,
                    persister=save_data,
                    run_async=run_async,
                    static_profile_id=static_profile_id
                )
        else:
            return await invoke_track_process_step_1(
                tracker_payload,
                source,
                ip=ip,
                profile_less=tracker_payload.profile_less,
                persister=save_data,
                run_async=run_async,
                static_profile_id=static_profile_id
            )

    except redis.exceptions.ConnectionError as e:
        raise TracardiException(f"Could not connect to Redis server. Connection returned error {str(e)}")


async def invoke_track_process_step_1(tracker_payload: TrackerPayload,
                                      source: EventSource,
                                      ip: str,
                                      profile_less: bool,
                                      persister: Callable,
                                      run_async: bool = False,
                                      static_profile_id: bool = False
                                      ) -> TrackerResult:
    tracker_payload.set_transitional(source)
    tracker_payload.set_return_profile(source)

    # Load session from storage
    try:
        if tracker_payload.session is not None:
            session = await cache.session(
                session_id=tracker_payload.session.id,
                ttl=memory_cache.session_cache_ttl
            )
        else:
            session = Session(id=str(uuid4()), metadata=SessionMetadata())
            tracker_payload.force_session(session)

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

    if static_profile_id is True:
        # Get static profile - This is dangerous
        profile, session = await tracker_payload.get_static_profile_and_session(
            session,
            storage.driver.profile.load_merged_profile,
            profile_less
        )
    else:
        # Get profile
        profile, session = await tracker_payload.get_profile_and_session(
            session,
            storage.driver.profile.load_merged_profile,
            profile_less
        )

    task = invoke_track_process_step_2(
        tracker_payload,
        source,
        profile_less,
        persister,  # Callable
        profile,
        session,
        ip)

    # todo do not know is makes sense - async
    if run_async:
        asyncio.create_task(task)
        return TrackerResult(
            tracker_payload=tracker_payload,
            response={
                "profile": {
                    "id": profile.id
                },
                "ux": [],
                "response": {}
            },
            events=[]
        )
    else:
        return await task


# Todo remove 2023-04-01 - obsolete
async def synchronized_event_tracking(tracker_payload: TrackerPayload, host: str, profile_less: bool,
                                      allowed_bridges: List[str], internal_source=None):
    tracker_payload.profile_less = profile_less
    return await track_event(tracker_payload,
                             ip=host,
                             allowed_bridges=allowed_bridges,
                             internal_source=internal_source)
