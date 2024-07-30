from typing import List

import time

from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.service.change_monitoring.field_change_logger import FieldChangeLogger
from tracardi.service.storage.elastic.interface.event import save_events_in_db
from tracardi.service.tracking.destination.dispatcher import sync_event_destination, sync_profile_destination
from tracardi.service.tracking.process.loading import tracker_loading
from tracardi.service.storage.elastic.interface.collector.mutation import profile as mutation_profile_db
from tracardi.service.tracking.storage.session_storage import save_session
from tracardi.service.tracking.track_data_computation import compute_data
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.triggers import exec_workflow

logger = get_logger(__name__)


async def os_tracker(
        field_change_logger: FieldChangeLogger,
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
        profile, session = await tracker_loading(tracker_payload, tracker_config)

        # Lock profile and session for changes and compute data
        profile, session, events, tracker_payload = await compute_data(
            profile,
            session,
            tracker_payload,
            tracker_config,
            source,
            field_change_logger
        )

        # Save profile
        if profile and profile.has_not_saved_changes():
            # Sync save
            await mutation_profile_db.save_profile(profile)

        # Save session
        if session and session.has_not_saved_changes():
            # Sync save
            await save_session(session)

        # Save events
        if events:
            # Sync save
            await save_events_in_db(events)

        try:

            # Clean up so can not be used. It is already in session
            if 'location' in tracker_payload.context:
                del tracker_payload.context['location']

            if 'utm' in tracker_payload.context:
                del tracker_payload.context['utm']

            # Dispatch events SYNCHRONOUSLY
            await sync_event_destination(
                profile,
                session,
                events,
                tracker_payload.debug)

            # Dispatch outbound profile SYNCHRONOUSLY
            timestamp_log: List[dict] = field_change_logger.convert_to_list(
                dict(
                    profile_id=get_entity_id(profile),
                    source_id=source.id,
                    session_id=get_entity_id(session),
                    request_id=get_context().id
                )
            )

            await sync_profile_destination(
                profile,
                session,
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
            workflow_result = await exec_workflow(
                get_entity_id(profile),
                session,
                events,
                tracker_payload)

            if workflow_result is not None:  # Workflow feature enabled

                profile, session, events, ux, response, wf_changed_fields, is_wf_triggered = workflow_result

                if is_wf_triggered and not wf_changed_fields.empty():

                    _changed_fields = wf_changed_fields.convert_to_list({
                        "profile_id": profile.id,
                        "session_id": session.id,
                        "request_id": get_context().id
                    })

                    # Save changes to field log
                    if tracardi.enable_field_update_log:
                        # Save to history if needed (DISABLE to REDO)
                        # await profile_change_log_worker(_changed_fields)
                        pass

                    # Dispatch profile changed outbound traffic if profile changed in workflow
                    # Send it SYNCHRONOUSLY

                    await sync_profile_destination(
                        profile,
                        session,
                        changed_fields=_changed_fields
                    )

            return {
                "task": tracker_payload.get_id(),
                "ux": ux,
                "response": response,
                "events": [event.id for event in events] if tracker_payload.is_debugging_on() else [],
                "profile": {
                    "id": get_entity_id(profile)
                },
                "session": {
                    "id": get_entity_id(session)
                },
                "errors": [],
                "warnings": []
            }
        finally:
            # TODO this is probably not needed
            if profile and profile.metadata.system.has_merging_data():
                pass
    finally:
        logger.debug(f"Process time {time.time() - tracking_start}")
