import time
from tracardi.service.tracking.track_data_computation import lock_and_compute_data
from tracardi.service.tracking.track_dispatching import dispatch_sync_workflow_and_destinations
from tracardi.service.tracking.tracker_persister_async import TrackingPersisterAsync
from tracardi.context import get_context
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id

logger = get_logger(__name__)
cache = CacheManager()


async def os_tracker(source: EventSource,
                             tracker_payload: TrackerPayload,
                             tracker_config: TrackerConfig,
                             tracking_start: float,
                             console_log: ConsoleLog
                             ):
    try:

        if not tracker_payload.events:
            logger.debug(f"No events have been sent in tracker payload.")
            return None

        # Lock profile and session for changes and compute data

        profile, session, events, tracker_payload, field_timestamp_monitor = await lock_and_compute_data(
            tracker_payload,
            tracker_config,
            source,
            console_log
        )

        try:
            if profile:
                logger.debug(f"Profile {get_entity_id(profile)} cached in context {get_context()}")

            # Clean up
            if 'location' in tracker_payload.context:
                del tracker_payload.context['location']

            if 'utm' in tracker_payload.context:
                del tracker_payload.context['utm']

            # ----------------------------------------------
            # FROM THIS POINT EVENTS AND SESSION SHOULD NOT BE MUTATED
            # ----------------------------------------------

            # Compute process time

            for event in events:
                event.metadata.time.total_time = time.time() - tracking_start

            # Save events

            storage = TrackingPersisterAsync()
            await storage.save_events(events)

            # TODO this should be in mutex as is mutates profile

            profile, session, events, ux, response = await (
                dispatch_sync_workflow_and_destinations(
                    profile,
                    session,
                    events,
                    tracker_payload,
                    console_log,
                    # Save. We need to manually save the session and profile in Open-source as there is no
                    # flusher worker and in-memory profile and session is not saved
                    store_in_db=True,  # No cache worker for OS. must store manually
                    storage=storage
                ))

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
