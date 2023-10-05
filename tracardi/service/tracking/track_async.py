import time
import logging

from tracardi.service.license import License
from tracardi.service.tracking.cache.profile_cache import save_profile_cache
from tracardi.service.tracking.cache.session_cache import save_session_cache
from tracardi.service.tracking.locking import GlobalMutexLock
from tracardi.service.tracking.system_events import add_system_events
from tracardi.service.tracking.track_data_computation import compute_data
from tracardi.service.tracking.track_dispatching import dispatch_sync
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
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id

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

                # MUST BE INSIDE MUTEX
                # Update only when needed

                if profile.operation.new or profile.operation.needs_update():
                    save_profile_cache(profile)

                if session.operation.new or session.operation.needs_update():
                    save_session_cache(session)

        else:

            profile, session, events, tracker_payload = await compute_data(
                tracker_payload,
                tracker_config,
                source,
                console_log
            )

            # Update only when needed

            if profile.operation.new or profile.operation.needs_update():
                save_profile_cache(profile)

            if session.operation.new or session.operation.needs_update():
                save_session_cache(session)

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
            event.metadata.time.total_time = time.time() - tracking_start

        # Async storage
        context = get_context()

        if License.has_license():

            if com_tracardi_settings.pulsar_host or com_tracardi_settings.async_processing:

                """
                Async processing can not do the following things:
                - Discard event or change as it is saved before the workflow kicks off
                - Save any properties such as processed_by property as processing happens in parallel to saving
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

                profile, session, events, ux, response = await dispatch_sync(
                    source,
                    profile,
                    session,
                    events,
                    tracker_payload,
                    tracker_config,
                    console_log
                )

        else:

            profile, session, events, ux, response = await dispatch_sync(
                source,
                profile,
                session,
                events,
                tracker_payload,
                tracker_config,
                console_log
            )

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
