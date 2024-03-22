from typing import List, Optional, Tuple, Union, Set

from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.change_monitoring.field_change_monitor import FieldChangeTimestampManager
from tracardi.service.field_mappings_cache import add_new_field_mappings
from tracardi.service.storage.elastic.interface.session import save_session_to_db
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.cache.profile_cache import save_profile_cache
from tracardi.service.tracking.cache.session_cache import save_session_cache
from tracardi.service.tracking.destination.dispatcher import sync_profile_destination
from tracardi.service.tracking.locking import Lock, async_mutex
from tracardi.service.tracking.storage.profile_storage import load_profile
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.tracking.workflow_manager_async import WorkflowManagerAsync, TrackerResult
from tracardi.service.storage.driver.elastic import profile as profile_db
from tracardi.service.storage.driver.elastic import field_update_log as field_update_log_db

logger = get_logger(__name__)
_redis = RedisClient()


async def _save_profile(profile: Profile):
    save_profile_cache(profile)
    # Save to database - do not defer
    await profile_db.save(profile, refresh_after_save=True)


async def _save_session(sessions: Union[Session, List[Session], Set[Session]]):
    context = get_context()
    save_session_cache(sessions, context)
    # Save to database - do not defer
    await save_session_to_db(sessions)


async def trigger_workflows(profile: Profile,
                            session: Session,
                            events: List[Event],
                            tracker_payload: TrackerPayload,
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

    is_wf_triggered = isinstance(tracker_result, TrackerResult) and tracker_result.wf_triggered

    if is_wf_triggered:
        # Add new fields to field mapping. New fields can be created in workflow.
        add_new_field_mappings(profile, session)

    if auto_merge_ids:
        profile.metadata.system.set_auto_merge_fields(auto_merge_ids)

    return profile, session, events, ux, response, field_manager, is_wf_triggered


async def _exec_workflow(profile_id: Optional[str], session: Session, events: List[Event], tracker_payload: TrackerPayload) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], FieldChangeTimestampManager, bool]:

    # Loads profile form cache
    # Profile needs to be loaded from cache. It may have changed during it was dispatched by event trigger

    profile: Profile = await load_profile(profile_id) if profile_id is not None else None

    # Triggers workflow

    profile, session, events, ux, response, field_change_manager, is_wf_triggered = await (
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
            await _save_profile(profile)

        if session and session.is_updated_in_workflow():
            logger.debug(f"Session {session.id} needs update after workflow.")

            # Profile is in mutex, that means no session for the profile should be modified.
            # No session loading from cache necessary; Save it in db and cache
            # Synchronous save
            await _save_session(session)

        if field_change_manager.has_changes():

            # Save changes to field log
            if tracardi.enable_field_update_log:
                log = field_change_manager.get_history_log()
                await field_update_log_db.upsert(log)

            # Dispatch profile changed outbound traffic if profile changed in workflow
            # Send it SYNCHRONOUSLY

            changed_fields = field_change_manager.get_history_log(add_id=False)
            await sync_profile_destination(
                profile,
                session,
                changed_fields
            )

    return profile, session, events, ux, response, field_change_manager, is_wf_triggered


async def exec_workflow(profile_id: Optional[str], session: Session, events: List[Event], tracker_payload: TrackerPayload) -> Tuple[
    Profile, Session, List[Event], Optional[list], Optional[dict], FieldChangeTimestampManager, bool]:

    if tracardi.enable_workflow:

        if profile_id is None:
            # Profile less execution
            return await _exec_workflow(
                profile_id, session, events, tracker_payload
            )

        profile_key = Lock.get_key(Collection.lock_tracker, "profile", profile_id)
        profile_lock = Lock(_redis, profile_key, default_lock_ttl=5)

        async with async_mutex(profile_lock, name='workflow-worker'):
            profile, session, events, ux, response, field_change_manager, is_wf_triggered = await _exec_workflow(
                profile_id, session, events, tracker_payload
            )

        # logger.info(f"Output profile {profile.traits}")
        # logger.info(f"Output session {session}")
        # logger.info(f"Output events {events}")
        # logger.info(f"Output ux {ux}")
        # logger.info(f"Output response {response}")

        return profile, session, events, ux, response, field_change_manager, is_wf_triggered