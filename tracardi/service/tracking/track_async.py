from datetime import timedelta, datetime

import time
import logging

from tracardi.domain.session import FrozenSession
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

if License.has_service(LICENSE):
    from com_tracardi.config import com_tracardi_settings
    from com_tracardi.service.tracking.track_dispatcher import dispatch_events_wf_destinations_async
    from com_tracardi.service.tracking.visti_end_dispatcher import schedule_visit_end_check
    from com_tracardi.service.tracking.field_change_dispatcher import field_update_log_dispatch

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

        profile, session, events, tracker_payload, field_timestamp_monitor = await lock_and_compute_data(
            tracker_payload,
            tracker_config,
            source,
            console_log
        )

        logger.info(f"Profile {get_entity_id(profile)} cached in context {get_context()}")

        # Clean up
        if 'location' in tracker_payload.context:
            del tracker_payload.context['location']

        if 'utm' in tracker_payload.context:
            del tracker_payload.context['utm']

        # ----------------------------------------------
        # FROM THIS POINT EVENTS AND SESSION SHOULD NOT BE MUTATED
        # ----------------------------------------------

        session = FrozenSession(**session.model_dump())

        # Async storage

        # Get context for queue

        dispatch_context = get_context().get_user_less_context_copy()

        if License.has_service(LICENSE):

            # Queue updated fields as field update history log.
            # Queues only updates made in mapping. Updates made in workflow are queued either
            # in worker of after workflow.


            if tracardi.enable_field_update_log and field_timestamp_monitor:
                timestamp_log = field_timestamp_monitor.get_timestamps_log()
                if timestamp_log.has_changes():
                    field_update_log_dispatch(dispatch_context, timestamp_log.get_history_log())

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
                },
                "session": {
                    "id": get_entity_id(session)
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
                    logger.info(f"Scheduled visit end check with task {task} for profile {profile.id}. "
                                f"Kicks off at {datetime.utcnow()+ timedelta(seconds=60 * 5)}")

                if async_events:

                    """
                    Async processing can not do the following things:
                    - Discard event or change as it is saved before the workflow kicks off
                    - Save any properties such as processed_by property as processing happens in parallel to saving
                    - Return response and ux as processing happens in parallel with response
                    """
                    print('async', [e.type for e in async_events], dispatch_context)

                    # Pulsar publish

                    # TODO merge profile_field_timestamps this is from mapping

                    dispatch_events_wf_destinations_async(
                        dispatch_context,
                        source,
                        profile,
                        session,
                        async_events,
                        tracker_payload,
                        tracker_config
                    )

                    result["task"].append(tracker_payload.get_id())
                    result['events'] += [event.id for event in sync_events]
            else:
                # If disabled async storing or no pulsar add async events to sync and run it
                sync_events += async_events

            # Sync events. Events that are marked as async: false

            if sync_events:

                # Save events - should not be mutated

                storage = TrackingPersisterAsync()
                events_result = await storage.save_events(sync_events)
                print("save_sync_result", events_result, get_context())

                # TODO Do not know if destinations are needed here. They are also dispatched in async

                profile, session, sync_events, ux, response = await (
                    dispatch_sync_workflow_and_destinations(
                        profile,
                        session,
                        sync_events,
                        tracker_payload,
                        console_log,
                        # We save manually only when async processing is disabled. Disabled async it will not
                        # be processed by async storage worker. Otherwise flusher worker saves in-memory profile
                        # and session automatically
                        store_in_db=com_tracardi_settings.async_processing is False,
                        storage=storage
                    )
                )

                result['ux'] = ux
                result['response'] = response
                result['events'] += [event.id for event in sync_events]

            return result

        else:

            # Open-source version

            # Compute process time

            for event in events:
                event.metadata.time.total_time = time.time() - tracking_start

            # Save events

            storage = TrackingPersisterAsync()
            events_result = await storage.save_events(events)

            profile, session, events, ux, response = await (
                dispatch_sync_workflow_and_destinations(
                    profile,
                    session,
                    events,
                    tracker_payload,
                    console_log,
                    # Save. We need to manually save the session and profile in Open-source as there is no
                    # flusher worker and in-memory profile and session is not saved
                    store_in_db=True,  # No cache worker for OS. mus store manually
                    storage=storage
                ))

        return {
            "task": tracker_payload.get_id(),
            "ux": ux,
            "response": response,
            "profile": {
                "id": get_entity_id(profile)
            },
            "session": {
                "id": get_entity_id(session)
            }
        }

    finally:
        print("track_async", time.time() - tracking_start, flush=True)
        print("---------------------", flush=True)
