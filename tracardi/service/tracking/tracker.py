import time

from tracardi.service.tracking.destination.dispatcher import sync_event_destination, sync_profile_destination
from tracardi.service.tracking.track_data_computation import lock_and_compute_data
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache_manager import CacheManager
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.triggers import exec_workflow
from tracardi.service.storage.driver.elastic import field_update_log as field_update_log_db

logger = get_logger(__name__)
cache = CacheManager()


async def os_tracker(source: EventSource,
                     tracker_payload: TrackerPayload,
                     tracker_config: TrackerConfig,
                     tracking_start: float
                     ):
    try:

        if not tracker_payload.events:
            logger.debug(f"No events have been sent in tracker payload.")
            return None

        # Lock profile and session for changes and compute data
        # Saves session, profile, events
        profile, session, events, tracker_payload, field_timestamp_monitor = await lock_and_compute_data(
            tracker_payload,
            tracker_config,
            source
        )

        # TODO maybe should be moved to lock_and_compute_data
        if field_timestamp_monitor:
            timestamp_log = field_timestamp_monitor.get_timestamps_log()
            await field_update_log_db.upsert(timestamp_log.get_history_log())

        try:
            # TODO why is this here
            # Clean up
            if 'location' in tracker_payload.context:
                del tracker_payload.context['location']

            if 'utm' in tracker_payload.context:
                del tracker_payload.context['utm']

            # ----------------------------------------------
            # FROM THIS POINT EVENTS AND SESSION SHOULD NOT
            # BE MUTATED, ALREADY SAVED
            # ----------------------------------------------

            # MUTEX: Session and profile are saved if workflow triggered
            profile, session, events, ux, response, field_changes, is_wf_triggered = await exec_workflow(profile.id,
                                                                                                         session,
                                                                                                         events,
                                                                                                         tracker_payload)

            # Dispatch events SYNCHRONOUSLY
            await sync_event_destination(
                profile,
                session,
                events,
                tracker_payload.debug)

            # Dispatch outbound profile SYNCHRONOUSLY
            await sync_profile_destination(profile, session)

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
            # print(0, profile.has_not_saved_changes(), profile.need_auto_merging())
            if profile and profile.metadata.system.has_merging_data():
                pass
            #     print(1, profile.ids)
            #     print(2, profile.get_auto_merge_ids())
    finally:
        logger.debug(f"Process time {time.time() - tracking_start}")
