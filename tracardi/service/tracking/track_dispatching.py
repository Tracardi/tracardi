from typing import List

import logging

from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracking.destination.destination_dispatcher import ProfileDestinationDispatcher
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
                        console_log: ConsoleLog):
    print('SYNC')

    ux = []
    response = {}

    # This is MUST BE FIRST BEFORE WORKFLOW
    profile_dispatcher = ProfileDestinationDispatcher(profile, console_log)

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
