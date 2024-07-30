from typing import List, Optional, Tuple, Dict

from tracardi.config import tracardi
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.change_monitoring.field_change_logger import FieldChangeLogger
from tracardi.service.field_mappings_cache import add_new_field_mappings
from tracardi.service.storage.elastic.interface.collector.mutation.profile import save_profile_in_db_and_cache
from tracardi.service.storage.elastic.interface.collector.mutation.session import save_session_to_db_and_cache
from tracardi.service.storage.elastic.interface.collector.load.profile import load_profile
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.tracking.workflow_manager_async import WorkflowManagerAsync, TrackerResult

logger = get_logger(__name__)


async def trigger_workflows(profile: Profile,
                            session: Session,
                            events: List[Event],
                            tracker_payload: TrackerPayload,
                            debug: bool) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], Dict[str, List], bool]:
    # Checks rules and trigger workflows for given events and saves profile and session

    ux = []
    response = {}
    auto_merge_ids = set()
    tracker_result = None

    if tracardi.enable_workflow:
        tracking_manager = WorkflowManagerAsync(
            tracker_payload,
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

        # Set fields timestamps

        if profile:
            _auto_merge_ids = profile.set_metadata_fields_timestamps(tracker_result.changed_field_timestamps)
            if _auto_merge_ids:
                auto_merge_ids = auto_merge_ids.union(_auto_merge_ids)

    is_wf_triggered = isinstance(tracker_result, TrackerResult) and tracker_result.wf_triggered

    if is_wf_triggered:
        # Add new fields to field mapping. New fields can be created in workflow.
        add_new_field_mappings(profile, session)

    if auto_merge_ids:
        profile.metadata.system.set_auto_merge_fields(auto_merge_ids)

    return profile, session, events, ux, response, tracker_result.changed_field_timestamps, is_wf_triggered


async def _exec_workflow(profile_id: Optional[str], session: Session, events: List[Event],
                         tracker_payload: TrackerPayload) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], FieldChangeLogger, bool]:
    # Loads profile form cache
    # Profile needs to be loaded from cache. It may have changed during it was dispatched by event trigger

    profile: Profile = await load_profile(profile_id) if profile_id is not None else None

    # Triggers workflow

    profile, session, events, ux, response, changed_fields, is_wf_triggered = await (
        # Triggers all workflows for given events
        trigger_workflows(profile,
                          session,
                          events,
                          tracker_payload,
                          debug=False)
    )

    # Saves if changed

    if is_wf_triggered:

        # Save to cache after processing. This is needed when both async and sync workers are working
        # The state should always be in cache.

        if profile and profile.is_updated_in_workflow():
            logger.debug(f"Profile {profile.id} needs update after workflow.")

            # Profile is in mutex, no profile loading from cache necessary; Save it in db and cache
            # Synchronous save
            await save_profile_in_db_and_cache(profile)

        if session and session.is_updated_in_workflow():
            logger.debug(f"Session {session.id} needs update after workflow.")

            # Profile is in mutex, that means no session for the profile should be modified.
            # No session loading from cache necessary; Save it in db and cache
            # Synchronous save
            await save_session_to_db_and_cache(session)

        changed_fields = FieldChangeLogger(changed_fields)

    return profile, session, events, ux, response, changed_fields, is_wf_triggered


async def exec_workflow(profile_id: Optional[str], session: Session, events: List[Event],
                        tracker_payload: TrackerPayload) -> Optional[Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], FieldChangeLogger, bool]]:
    if not tracardi.enable_workflow:
        return None

    if profile_id is None:
        # Profile less execution
        return await _exec_workflow(
            profile_id, session, events, tracker_payload
        )

    profile, session, events, ux, response, workflow_field_timestamp_log, is_wf_triggered = await _exec_workflow(
        profile_id, session, events, tracker_payload
    )

    return profile, session, events, ux, response, workflow_field_timestamp_log, is_wf_triggered
