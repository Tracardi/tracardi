from typing import List, Tuple, Optional
from tracardi.service.change_monitoring.field_change_monitor import FieldChangeTimestampManager
from tracardi.service.license import License, LICENSE
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.ephemerals import remove_ephemeral_data
from tracardi.service.tracking.tracker_persister_async import TrackingPersisterAsync
from tracardi.context import get_context
from tracardi.service.console_log import ConsoleLog
from tracardi.service.field_mappings_cache import add_new_field_mappings
from tracardi.service.tracking.cache.merge_profile_cache import lock_merge_with_cache_and_save_profile
from tracardi.service.tracking.cache.merge_session_cache import lock_merge_with_cache_and_save_session
from tracardi.service.tracking.destination.destination_dispatcher import ProfileDestinationDispatcher
from tracardi.service.tracking.workflow_manager_async import WorkflowManagerAsync, TrackerResult
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache_manager import CacheManager
from tracardi.service.destinations.dispatchers import event_destination_dispatch
from tracardi.service.segments.post_event_segmentation import post_ev_segment
from tracardi.service.storage.driver.elastic import segment as segment_db
from tracardi.domain.event import Event
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session

if License.has_service(LICENSE) :
    from com_tracardi.service.tracking.field_change_dispatcher import field_update_log_dispatch

logger = get_logger(__name__)
cache = CacheManager()
_redis = RedisClient()

async def trigger_workflows(profile: Profile,
                            session: Session,
                            events: List[Event],
                            tracker_payload: TrackerPayload,
                            console_log: ConsoleLog,
                            debug: bool) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], FieldChangeTimestampManager, bool]:

    # Checks rules and trigger workflows for given events and saves profile and session

    ux = []
    response = {}
    auto_merge_ids = set()
    tracker_result = None
    field_manager = FieldChangeTimestampManager()

    if tracardi.enable_workflow:
        tracking_manager = WorkflowManagerAsync(
            console_log,
            tracker_payload,
            field_manager,
            profile,
            session
        )

        tracker_result = await tracking_manager.trigger_workflows_for_events(events, debug)

        # Reassign results

        profile = tracker_result.profile
        session = tracker_result.session
        events = tracker_result.events
        ux = tracker_result.ux
        response = tracker_result.response
        field_manager = tracker_result.changed_field_timestamps

        # Set fields timestamps

        if profile:
            _auto_merge_ids = profile.set_metadata_fields_timestamps(tracker_result.changed_field_timestamps)
            if _auto_merge_ids:
                auto_merge_ids = auto_merge_ids.union(_auto_merge_ids)


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


    if auto_merge_ids:
        profile.metadata.system.set_auto_merge_fields(auto_merge_ids)

    return profile, session, events, ux, response, field_manager, is_wf_triggered


async def dispatch_sync_workflow_and_destinations_and_save_data(profile: Profile,
                                                                session: Session,
                                                                events: List[Event],
                                                                tracker_payload: TrackerPayload,
                                                                console_log: ConsoleLog,
                                                                store_in_db: bool,
                                                                storage: TrackingPersisterAsync
                                                                ) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict]]:

    # This is MUST BE FIRST BEFORE WORKFLOW

    profile_dispatcher = ProfileDestinationDispatcher(profile, console_log)

    # Dispatch workflow and post eve segmentation

    profile, session, events, ux, response, field_update_log_manager, is_wf_triggered = await (
        trigger_workflows(
            profile,
            session,
            events,
            tracker_payload,
            console_log,
            False
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
                                                         lock_name="post-workflow-profile-save")

        if session and session.is_updated_in_workflow():
            # Locks session, loads session from cache merges it with current session and saves it in cache

            logger.info(f"Session needs update after workflow.")

            await lock_merge_with_cache_and_save_session(session,
                                                         context=get_context(),
                                                         lock_name="post-workflow-session-save")

    # Queue storage of fields update history log (changes made by workflow)

    if tracardi.enable_field_update_log and License.has_service(LICENSE) and field_update_log_manager.has_changes():
        field_update_log_dispatch(get_context(), field_update_log_manager.get_history_log())

    # We save manually only when async processing is disabled.
    # Otherwise, flusher worker saves in-memory profile and session automatically

    if tracardi.enable_event_destinations:
        load_destination_task = cache.event_destination
        await event_destination_dispatch(
            load_destination_task,
            profile,
            session,
            events,
            tracker_payload.debug
        )

    # Storage must be here as destination may need to load profile

    _profile_not_ephemeral, _session_not_ephemeral, _events_not_ephemeral = remove_ephemeral_data(tracker_payload,
                                                                                                  profile, session,
                                                                                                  events)

    if store_in_db:
        await storage.save_profile_and_session(
            _session_not_ephemeral,
            _profile_not_ephemeral
        )

    # Dispatch outbound profile

    await profile_dispatcher.dispatch(
        profile,
        session,
        events
    )

    return profile, session, events, ux, response
