from tracardi.service.change_monitoring.field_change_monitor import FieldChangeTimestampManager
from tracardi.service.tracking.tracker_persister_async import TrackingPersisterAsync
from typing import List, Tuple, Optional

import logging

from tracardi.context import get_context
from tracardi.service.console_log import ConsoleLog
from tracardi.service.field_mappings_cache import add_new_field_mappings
from tracardi.service.tracking.cache.profile_cache import lock_merge_with_cache_and_save_profile
from tracardi.service.tracking.cache.session_cache import lock_merge_with_cache_and_save_session
from tracardi.service.tracking.destination.destination_dispatcher import ProfileDestinationDispatcher
from tracardi.service.tracking.workflow_manager_async import WorkflowManagerAsync, TrackerResult
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from tracardi.service.destinations.dispatchers import event_destination_dispatch
from tracardi.service.segments.post_event_segmentation import post_ev_segment
from tracardi.service.storage.driver.elastic import segment as segment_db
from tracardi.domain.event import Event
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


async def trigger_workflows(profile: Profile,
                            session: Session,
                            events: List[Event],
                            tracker_payload: TrackerPayload,
                            console_log: ConsoleLog,
                            debug: bool) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], bool]:

    # Checks rules and trigger workflows for given events and saves profile and session

    ux = []
    response = {}
    tracker_result = None

    if tracardi.enable_workflow:
        tracking_manager = WorkflowManagerAsync(
            console_log,
            tracker_payload,
            FieldChangeTimestampManager(),
            profile,
            session
        )

        tracker_result = await tracking_manager.trigger_workflows_for_events(events, debug)

        # Reassign results

        profile = tracker_result.profile
        session = tracker_result.session
        events = tracker_result.events
        ux = tracker_result.ux,
        response = tracker_result.response

        # Set fields timestamps

        profile.metadata.set_fields_timestamps(tracker_result.changed_field_timestamps)

        # Dispatch changed profile to destination

    # Post Event Segmentation

    if tracardi.enable_post_event_segmentation and isinstance(profile, Profile):
        # MUTATES Profile

        await post_ev_segment(profile,
                              session,
                              [event.type for event in events],
                              segment_db.load_segments)

    is_wf_triggered = isinstance(tracker_result, TrackerResult) and tracker_result.wf_triggered

    if is_wf_triggered:

        # Add new fields to field mapping. New fields can be created in workflow.
        add_new_field_mappings(profile, session)


    return profile, session, events, ux, response, is_wf_triggered


async def dispatch_sync_workflow_and_destinations(profile: Profile,
                                                  session: Session,
                                                  events: List[Event],
                                                  tracker_payload: TrackerPayload,
                                                  console_log: ConsoleLog,
                                                  store_in_db:bool,
                                                  storage: TrackingPersisterAsync
                                                  ) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict]]:

    # This is MUST BE FIRST BEFORE WORKFLOW

    profile_dispatcher = ProfileDestinationDispatcher(profile, console_log)

    # Dispatch workflow and post eve segmentation

    debug = tracker_payload.is_on('debugger', default=False)

    profile, session, events, ux, response, is_wf_triggered = await (
        trigger_workflows(
            profile,
            session,
            events,
            tracker_payload,
            console_log,
            debug
        )
    )

    # INFO! trigger_workflows will SAVE changed profile and session in the cache. For the async this is
    # enough to persist data.

    if is_wf_triggered:

        # Save to cache after processing. This is needed when both async and sync workers are working
        # The state should always be in cache.

        if profile and profile.is_updated_in_workflow():
            # Locks profile, loads profile from cache merges it with current profile and saves it in cache

            logger.info(f"Profile needs update after workflow.")

            await lock_merge_with_cache_and_save_profile(profile,
                                                         context=get_context(),
                                                         lock_name="post-workflow-profile-save")

        if session and session.is_updated_in_workflow():
            # Locks session, loads session from cache merges it with current session and saves it in cache

            logger.info(f"Session needs update after workflow.")

            await lock_merge_with_cache_and_save_session(session,
                                                         context=get_context(),
                                                         lock_name="post-workflow-session-save")

    # We save manually only when async processing is disabled.
    # Otherwise, flusher worker saves in-memory profile and session automatically

    if store_in_db:

        profile_and_session_result = await storage.save_profile_and_session(
            session,
            profile
        )

    # Dispatch outbound events

    if tracardi.enable_event_destinations:
        load_destination_task = cache.event_destination
        await event_destination_dispatch(
            load_destination_task,
            profile,
            session,
            events,
            tracker_payload.debug
        )

    # Dispatch outbound profile

    await profile_dispatcher.dispatch(
        profile,
        session,
        events
    )

    return profile, session, events, ux, response
