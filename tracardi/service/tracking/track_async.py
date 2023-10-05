import time
import logging

from tracardi.service.license import License
from tracardi.service.tracking.destination.destination_dispatcher import ProfileDestinationDispatcher
from tracardi.service.tracking.locking import GlobalMutexLock
from tracardi.service.tracking.system_events import add_system_events
from tracardi.service.tracking.track_data_computation import compute_data
from tracardi.service.tracking.tracker_event_reshaper import EventsReshaper
from tracardi.service.tracking.event_validation import validate_events
from tracardi.service.tracking.tracker_persister_async import TrackingPersisterAsync
from tracardi.service.tracking.workflow_orchestrator_async import WorkflowOrchestratorAsync
from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.service.destinations.dispatchers import event_destination_dispatch
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.segments.post_event_segmentation import post_ev_segment
from tracardi.service.storage.driver.elastic import segment as segment_db

if License.has_license():
    from com_tracardi.config import com_tracardi_settings
    from com_tracardi.service.tracking.track_dispatcher import dispatch_async

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

        if tracardi.enable_event_validation:
            # Validate events. Checks validators and its conditions and sets validation status.

            # Event payload will be filled with validation status. Mutates tracker_payload
            tracker_payload = await validate_events(tracker_payload)

        if tracardi.enable_event_reshaping:
            # Reshape valid events

            evh = EventsReshaper(tracker_payload)
            tracker_payload = await evh.reshape_events()

        # Lock profile and session for changes

        if tracardi.lock_on_data_computation:
            _redis = RedisClient()
            async with (
                GlobalMutexLock(get_entity_id(tracker_payload.profile),
                                'profile',
                                namespace=Collection.lock_tracker,
                                redis=_redis
                                ),
                GlobalMutexLock(get_entity_id(tracker_payload.session),
                                'session',
                                namespace=Collection.lock_tracker,
                                redis=_redis
                                )):

                # Always use GlobalUpdateLock to update profile and session

                profile, session, events, tracker_payload = await compute_data(
                    tracker_payload,
                    tracker_config,
                    source,
                    console_log
                )

        else:

            profile, session, events, tracker_payload = await compute_data(
                tracker_payload,
                tracker_config,
                source,
                console_log
            )

        # Updates/Mutations of tracker_payload

        # Add system events
        if tracardi.system_events:
            tracker_payload = add_system_events(profile, session, tracker_payload)

        # Clean up
        if 'location' in tracker_payload.context:
            del tracker_payload.context['location']

        if 'utm' in tracker_payload.context:
            del tracker_payload.context['utm']

        # Compute process time

        for event in events:
            event.metadata.time.process_time = time.time() - tracking_start

        # Async storage
        context = get_context()

        if License.has_license():

            if com_tracardi_settings.pulsar_host or com_tracardi_settings.async_processing:

                """
                Async processing can not do the following things:
                - Discard event or change as it is saved before the workflow kicks off
                - Save processed by property as processing happens in parallel to saving
                - Return response and ux as processing happens in parallel with response
                """

                # Pulsar publish

                print('ASYNC')

                dispatch_async(
                    context,
                    source,
                    profile,
                    session,
                    events,
                    tracker_payload,
                    tracker_config,
                    timestamp=tracking_start
                )

                return {
                    "task": tracker_payload.get_id(),
                    "ux": [],  # Async does not have ux
                    "response": {},  # Async does not have response
                    "profile": {
                        "id": profile.id
                    }
                }

            else:
                print('SYNC')
                pass

        else:

            print('SYNC')

            ux = []
            response = {}
            # Run event destination

            if tracardi.enable_event_destinations:
                load_destination_task = cache.event_destination
                await event_destination_dispatch(
                    load_destination_task,
                    profile,
                    session,
                    events,
                    tracker_payload.debug
                )

            if tracardi.enable_workflow:

                # This is the old way of dispatching profiles to destinations

                profile_dispatcher = ProfileDestinationDispatcher(profile, console_log)

                workflow = WorkflowOrchestratorAsync(
                    source,
                    tracker_config
                )

                # Start workflow
                debug = tracker_payload.is_on('debugger', default=False)

                tracker_result = await workflow.lock_and_invoke(
                    tracker_payload,
                    events,
                    profile,
                    session,
                    debug
                )

                # Reassign results

                profile = tracker_result.profile
                session = tracker_result.session
                events = tracker_result.events
                ux = tracker_result.ux,
                response = tracker_result.response

                # Dispatch changed profile to destination

                await profile_dispatcher.dispatch(
                    profile,
                    session,
                    events
                )

                # Post Event Segmentation

                if tracardi.enable_post_event_segmentation and isinstance(profile, Profile):
                    await post_ev_segment(profile,
                                          session,
                                          [event.type for event in events],
                                          segment_db.load_segments)

        # Save

        result = await TrackingPersisterAsync().save(
            session,
            profile,
            events
        )

        return {
            "task": tracker_payload.get_id(),
            "ux": ux,
            "response": response,
            "profile": {
                "id": profile.id
            }
        }

    finally:
        print("track_async", time.time() - tracking_start, flush=True)
        print("---------------------", flush=True)
