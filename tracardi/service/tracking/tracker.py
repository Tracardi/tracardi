from typing import List

import time

from tracardi.context import get_context
from tracardi.domain.flat_event import FlatEvent
from tracardi.service.dependency import *
from tracardi.service.tracking.destination.dispatcher import sync_event_destination, sync_profile_destination
from tracardi.service.tracking.process.loading import tracker_loading
from tracardi.service.collector.mutation import profile as mutation_profile_db
from tracardi.service.tracking.compute.session_computer import compute_session
from tracardi.service.tracking.storage.session_storage import save_session
from tracardi.service.tracking.track_data_computation import compute_data
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.tracker_config import TrackerConfig
from tracardi.common.tools.getters import get_entity_id
from tracardi.service.wf.triggers import exec_workflow

logger = get_logger(__name__)

def _exclude_ephemeral(flat_events: List[FlatEvent]):
    for flat_event in flat_events:
        if flat_event.get("config.saveEvent", True):
            yield flat_event

async def os_tracker(
        source: EventSource,
        tracker_payload: TrackerPayload,
        tracker_config: TrackerConfig,
        tracking_start: float
):
    try:

        if not tracker_payload.events:
            logger.warning(f"No events have been sent in tracker payload.")
            return None

        # Load profile and session
        is_static_profile_id = tracker_config.static_profile_id is True or tracker_payload.has_static_profile_id()
        flat_profile, session, tracker_profile, tracker_session = await tracker_loading(tracker_payload, is_static_profile_id)

        tracker_payload.profile = tracker_profile
        tracker_payload.session = tracker_session

        session = await compute_session(
            session,
            tracker_payload,
            tracker_config
        )

        # Lock profile and session for changes and compute data
        flat_profile, session, flat_events, tracker_payload = await compute_data(
            flat_profile,
            session,
            tracker_payload,
            source
        )

        # Recreate Profile from flat_profile, that was changed

        if flat_profile:

            # Save profile
            if flat_profile and flat_profile.has_not_saved_changes():

                # Apply APM Hashing
                flat_profile.hash_all_allowed_pii_as_ids()

                # Sync save
                await mutation_profile_db.save_flat_profile(flat_profile)

        # Save session
        if session and session.has_not_saved_changes():
            # Sync save
            await save_session(session)

        # Save events
        if flat_events:
            # Sync save
            await bd_collector_adapter.save_events(list(_exclude_ephemeral(flat_events)))

        # Clean up so can not be used. It is already in session
        if 'location' in tracker_payload.context:
            del tracker_payload.context['location']

        if 'utm' in tracker_payload.context:
            del tracker_payload.context['utm']

        # Dispatch events SYNCHRONOUSLY
        await sync_event_destination(
            flat_profile,
            session,
            flat_events,
            tracker_payload.debug)

        # Dispatch outbound profile SYNCHRONOUSLY
        timestamp_log: List[dict] = [
            {
                "field": field,
                "timestamp": timestamp,
                "old_value": old_value,
            }
            for field, (timestamp, old_value)
            in flat_profile.get_change_logger().changes()]

        await sync_profile_destination(
            flat_profile,
            timestamp_log
        )

        # ----------------------------------------------
        # FROM THIS POINT EVENTS AND SESSION SHOULD NOT
        # BE MUTATED, ALREADY SAVED
        # ----------------------------------------------

        # MUTEX: Session and profile are saved if workflow triggered
        # DESTINATION: Destination will be triggered if profile changes.

        ux = None
        response = None
        if tracardi.enable_workflow:

            workflow_result = await exec_workflow(
                get_entity_id(flat_profile),
                session,
                flat_events,
                tracker_payload)

            if workflow_result is not None:  # Workflow feature enabled

                profile, session, events, ux, response, changed_fields, is_wf_triggered = workflow_result

                if is_wf_triggered and bool(changed_fields):

                    _changed_fields: List[dict] = [
                        {"field": field, "timestamp": timestamp, "old_value": old_value}
                        for field, (timestamp, old_value)
                        in changed_fields.items()]

                    # Save changes to field log
                    if tracardi.enable_field_update_log:
                        # Save to history if needed (DISABLE to REDO)
                        # await profile_change_log_worker(_changed_fields)
                        pass

                    # Dispatch profile changed outbound traffic if profile changed in workflow
                    # Send it SYNCHRONOUSLY

                    await sync_profile_destination(
                        flat_profile,
                        changed_fields=_changed_fields
                    )

        return {
            "task": tracker_payload.get_id(),
            "ux": ux,
            "response": response,
            "events": [event.id for event in flat_events] if tracker_payload.is_debugging_on() else [],
            "profile": {
                "id": get_entity_id(flat_profile)
            },
            "session": {
                "id": get_entity_id(session)
            },
            "errors": [],
            "warnings": []
        }

    finally:
        logger.debug(f"Process time {time.time() - tracking_start}")
        get_context().profiler.measure("end")
        # get_context().profiler.report()
