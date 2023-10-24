import time
import logging

from tracardi.service.field_mappings_cache import add_new_field_mappings
from tracardi.service.license import License, LICENSE
from tracardi.service.tracking.track_data_computation import lock_and_compute_data
from tracardi.service.tracking.track_dispatching import dispatch_sync_workflow_and_destinations
from tracardi.service.tracking.tracker_event_reshaper import EventsReshaper
from tracardi.service.tracking.event_validation import validate_events
from tracardi.service.tracking.tracker_persister_async import TrackingPersisterAsync
from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id

if License.has_license():
    from com_tracardi.config import com_tracardi_settings
    from com_tracardi.service.tracking.track_dispatcher import dispatch_events_wf_destinations_async
    from com_tracardi.service.tracking.visti_end_dispatcher import schedule_visit_end_check

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


async def process_track_data(source: EventSource,
                             tracker_payload: TrackerPayload,
                             tracker_config: TrackerConfig,
                             tracking_start: float,
                             console_log: ConsoleLog
                             ):
    try:

        if not tracker_payload.events:
            return None

        # Validate events from tracker payload

        if tracardi.enable_event_validation:
            # Validate events. Checks validators and its conditions and sets validation status.

            # Event payload will be filled with validation status. Mutates tracker_payload
            tracker_payload = await validate_events(tracker_payload)

        if tracardi.enable_event_reshaping:

            # Reshape valid events

            evh = EventsReshaper(tracker_payload)
            tracker_payload = await evh.reshape_events()

        # Lock profile and session for changes and compute data

        profile, session, events, tracker_payload = await lock_and_compute_data(
            tracker_payload,
            tracker_config,
            source,
            console_log
        )

        # Clean up
        if 'location' in tracker_payload.context:
            del tracker_payload.context['location']

        if 'utm' in tracker_payload.context:
            del tracker_payload.context['utm']

        # ----------------------------------------------
        # FROM THIS POINT EVENTS SHOULD NOT BE MUTATED
        # ----------------------------------------------

        # Async storage

        dispatch_context = get_context().get_user_less_context_copy()

        if License.has_service(LICENSE):

            # Split events into async and not async. Compute process time

            async_events = []
            sync_events = []
            for event in events:
                event.metadata.time.total_time = time.time() - tracking_start
                is_async = event.config.get('async', True)
                if is_async:
                    async_events.append(event)
                else:
                    sync_events.append(event)

            # Delete events so it is no longer used by mistake. Use async_events or sync_events.
            events = None

            result = {
                "task": [],
                "ux": [],  # Async does not have ux
                "response": {},  # Async does not have response
                "events": [],
                "profile": {
                    "id": get_entity_id(profile)
                }
            }

            # Async events

            if com_tracardi_settings.pulsar_host and com_tracardi_settings.async_processing:

                # Track session for visit end

                if session and session.operation.new:
                    task = schedule_visit_end_check(
                        dispatch_context,
                        session,
                        profile,
                        source
                    )
                    logger.info(f"Scheduled visit end check with task {task} for profile {profile.id}")

                if async_events:

                    """
                    Async processing can not do the following things:
                    - Discard event or change as it is saved before the workflow kicks off
                    - Save any properties such as processed_by property as processing happens in parallel to saving
                    - Return response and ux as processing happens in parallel with response
                    """
                    print('async', [e.type for e in async_events], dispatch_context)

                    # Pulsar publish

                    dispatch_events_wf_destinations_async(
                        dispatch_context,
                        source,
                        profile,
                        session,
                        async_events,
                        tracker_payload,
                        tracker_config,
                        timestamp=tracking_start
                    )

                    result["task"].append(tracker_payload.get_id())
                    result['events'] += [event.id for event in sync_events]
            else:
                # If disabled async storing or no pulsar add async events to sync and run it
                sync_events += async_events

            # Sync events

            if sync_events:

                # Save events - should not be mutated

                storage = TrackingPersisterAsync()
                events_result = await storage.save_events(sync_events)
                print("save_sync_result", events_result, get_context())

                # TODO Do not know if destinations are needed here. They are also dispatched in async

                profile, session, sync_events, ux, response = await dispatch_sync_workflow_and_destinations(
                    source,
                    profile,
                    session,
                    sync_events,
                    tracker_payload,
                    tracker_config,
                    console_log
                )

                result['ux'] = ux
                result['response'] = response
                result['events'] += [event.id for event in sync_events]

                # We save manually only when async processing is disabled.
                # Otherwise flusher worker saves in-memory profile and session automatically

                if com_tracardi_settings.async_processing is False:

                    profile_and_session_result = await storage.save_profile_and_session(
                        session,
                        profile
                    )

            return result

        else:

            # Open-source version

            # Compute process time

            for event in events:
                event.metadata.time.total_time = time.time() - tracking_start

            # Save events

            storage = TrackingPersisterAsync()
            events_result = await storage.save_events(events)

            profile, session, events, ux, response = await dispatch_sync_workflow_and_destinations(
                source,
                profile,
                session,
                events,
                tracker_payload,
                tracker_config,
                console_log
            )

            # Save. We need to manually save the session and profile in Open-source as there is no
            # flusher worker and in-memory profile and session is not saved

            profile_and_session_result = await storage.save_profile_and_session(
                session,
                profile
            )

        return {
            "task": tracker_payload.get_id(),
            "ux": ux,
            "response": response,
            "profile": {
                "id": get_entity_id(profile)
            }
        }

    finally:
        print("track_async", time.time() - tracking_start, flush=True)
        print("---------------------", flush=True)
