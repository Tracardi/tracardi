from typing import List, Tuple, Optional

import logging

from tracardi.service.console_log import ConsoleLog
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.cache.profile_cache import save_profile_cache
from tracardi.service.tracking.cache.session_cache import save_session_cache
from tracardi.service.tracking.destination.destination_dispatcher import ProfileDestinationDispatcher
from tracardi.service.tracking.locking import GlobalMutexLock
from tracardi.service.tracking.workflow_orchestrator_async import WorkflowOrchestratorAsync
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from tracardi.service.destinations.dispatchers import event_destination_dispatch
from tracardi.service.segments.post_event_segmentation import post_ev_segment
from tracardi.service.storage.driver.elastic import segment as segment_db
from tracardi.domain.event import Event
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


async def dispatch_sync(source: EventSource,
                        profile: Profile,
                        session: Session,
                        events: List[Event],
                        tracker_payload: TrackerPayload,
                        tracker_config: TrackerConfig,
                        console_log: ConsoleLog) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict]]:

    ux = []
    response = {}

    if tracardi.enable_workflow:
        workflow = WorkflowOrchestratorAsync(
            source,
            tracker_config,
            console_log
        )

        # Start workflow
        debug = tracker_payload.is_on('debugger', default=False)

        tracker_result = await workflow.lock_and_invoke(
            tracker_payload,
            events,
            profile,
            session,
            debug
        )

        # Reassign results

        profile = tracker_result.profile
        session = tracker_result.session
        events = tracker_result.events
        ux = tracker_result.ux,
        response = tracker_result.response

        # Dispatch changed profile to destination

    # Post Event Segmentation

    if tracardi.enable_post_event_segmentation and isinstance(profile, Profile):
        # MUTATES Profile

        await post_ev_segment(profile,
                              session,
                              [event.type for event in events],
                              segment_db.load_segments)

    return profile, session, events, ux, response


async def lock_dispatch_sync(source: EventSource,
                             profile: Profile,
                             session: Session,
                             events: List[Event],
                             tracker_payload: TrackerPayload,
                             tracker_config: TrackerConfig,
                             console_log: ConsoleLog) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict]]:

    # This is MUST BE FIRST BEFORE WORKFLOW
    profile_dispatcher = ProfileDestinationDispatcher(profile, console_log)

    if tracardi.lock_on_data_computation:
        _redis = RedisClient()
        async with (
            GlobalMutexLock(get_entity_id(tracker_payload.profile),
                            'profile',
                            namespace=Collection.lock_tracker,
                            redis=_redis
                            ),
            GlobalMutexLock(get_entity_id(tracker_payload.session),
                            'session',
                            namespace=Collection.lock_tracker,
                            redis=_redis
                            )):

            # Dispatch
            profile, session, events, ux, response = await dispatch_sync(source,
                                                                         profile,
                                                                         session,
                                                                         events,
                                                                         tracker_payload,
                                                                         tracker_config,
                                                                         console_log)

            # Save to cache after processing. This is needed when both async and sync workers are working
            # The state should always be in cache. MUST BE INSIDE MUTEX

            if profile and (profile.operation.new or profile.operation.needs_update()):
                save_profile_cache(profile)

            if session and (session.operation.new or session.operation.needs_update()):
                save_session_cache(session)

    else:

        # Dispatch
        profile, session, events, ux, response = await dispatch_sync(source,
                                                                     profile,
                                                                     session,
                                                                     events,
                                                                     tracker_payload,
                                                                     tracker_config,
                                                                     console_log)

        # Save to cache after processing. This is needed when both async and sync workers are working
        # The state should always be in cache. MUST BE INSIDE MUTEX

        if profile.operation.new or profile.operation.needs_update():
            save_profile_cache(profile)

        if session.operation.new or session.operation.needs_update():
            save_session_cache(session)

    # Dispatch events

    if tracardi.enable_event_destinations:
        load_destination_task = cache.event_destination
        await event_destination_dispatch(
            load_destination_task,
            profile,
            session,
            events,
            tracker_payload.debug
        )

    # Dispatch profile

    await profile_dispatcher.dispatch(
        profile,
        session,
        events
    )

    return profile, session, events, ux, response
