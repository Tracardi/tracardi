from typing import Tuple, List, Optional

from tracardi.config import tracardi
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor
from tracardi.service.license import License
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.cache.profile_cache import save_profile_cache
from tracardi.service.tracking.cache.session_cache import save_session_cache
from tracardi.service.tracking.event_data_computation import compute_events
from tracardi.service.tracking.locking import GlobalMutexLock
from tracardi.service.tracking.profile_data_computation import update_profile_last_geo, update_profile_email_type, \
    update_profile_visits, update_profile_time
from tracardi.service.tracking.session_data_computation import compute_session, update_device_geo, \
    update_session_utm_with_client_data
from tracardi.service.tracking.profile_loading import load_profile_and_session
from tracardi.service.tracking.session_loading import load_or_create_session
from tracardi.service.tracking.system_events import add_system_events
from tracardi.service.tracking.tracker_persister_async import clear_relations

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload

from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id

if License.has_license():
    from com_tracardi.service.data_compliance import event_data_compliance
    from com_tracardi.service.identification_point_service import identify_and_merge_profile


async def compute_data(tracker_payload: TrackerPayload,
                       tracker_config: TrackerConfig,
                       source: EventSource,
                       console_log: ConsoleLog) -> Tuple[Profile, Optional[Session], List[Event], TrackerPayload,
Optional[FieldTimestampMonitor]]:

    # We need profile and session before async

    session, tracker_payload = await load_or_create_session(tracker_payload)

    # Load profile

    profile, session = await load_profile_and_session(
        session,
        tracker_config,
        tracker_payload,
        console_log
    )

    if License.has_license():
        if profile is not None:

            # Anonymize, data compliance

            event_payloads, compliance_errors = await event_data_compliance(
                profile,
                event_payloads=tracker_payload.events)

            # Reassign events as there may be changes
            tracker_payload.events = event_payloads

            for error in compliance_errors:
                console_log.append(error)

            # Merge profile on identification points

            identification_points = list(await tracker_payload.get_identification_points())

            profile, event_payloads = await identify_and_merge_profile(profile,
                                                                       identification_points,
                                                                       tracker_payload.events,
                                                                       console_log)

            # Save event payload
            tracker_payload.events = event_payloads

    # ------------------------------------
    # Session and events computation

    # Is new session
    if session.operation.new:
        # Compute session. Session is filled only when new
        session, profile = compute_session(
            session,
            profile,
            tracker_payload,
            tracker_config
        )

    # Update missing data
    session = await update_device_geo(tracker_payload, session)
    session = update_session_utm_with_client_data(tracker_payload, session)

    # Profile computation

    if profile:
        # Update profile last geo with session device geo
        profile = update_profile_last_geo(session, profile)

        # Update email type
        profile = update_profile_email_type(profile)

        # Update visits
        profile = update_profile_visits(session, profile)

        # Update profile time zone
        profile = update_profile_time(session, profile)

    # Updates/Mutations of tracker_payload and session

    # Add system events
    if tracardi.system_events:
        tracker_payload, session = add_system_events(profile, session, tracker_payload)

    # ---------------------------------------------------------------------------
    # Compute events. Session can be changed if there is event e.g. visit-open
    # This should be last in the process. We need all data for event computation
    # events, session, profile = None, None, []
    # Profile has fields timestamps updated

    events, session, profile, field_timestamp_monitor = await compute_events(
        tracker_payload.events,  # All events with system events, and validation information
        tracker_payload.metadata,
        source,
        session,
        profile,
        tracker_payload.profile_less,
        console_log,
        tracker_payload
    )

    # Clear profile,etc if not saving data.

    profile, session, events = clear_relations(tracker_payload, profile, session, events)

    # Caution: After clear session can become None if set sessionSave = False

    return profile, session, events, tracker_payload, field_timestamp_monitor


async def lock_and_compute_data(
        tracker_payload: TrackerPayload,
        tracker_config: TrackerConfig,
        source: EventSource,
        console_log: ConsoleLog) -> Tuple[Profile, Session, List[Event], TrackerPayload, Optional[FieldTimestampMonitor]]:

    if tracardi.lock_on_data_computation:
        _redis = RedisClient()
        async with (
            GlobalMutexLock(get_entity_id(tracker_payload.profile),
                            'profile',
                            namespace=Collection.lock_tracker,
                            redis=_redis,
                            name='lock_and_compute_data'
                            ),
            GlobalMutexLock(get_entity_id(tracker_payload.session),
                            'session',
                            namespace=Collection.lock_tracker,
                            redis=_redis,
                            name='lock_and_compute_data'
                            )):

            # Always use GlobalUpdateLock to update profile and session

            profile, session, events, tracker_payload, field_timestamp_monitor = await compute_data(
                tracker_payload,
                tracker_config,
                source,
                console_log
            )

            # MUST BE INSIDE MUTEX
            # Update only when needed

            if profile and profile.has_not_saved_changes():
                save_profile_cache(profile)

            if session and session.has_not_saved_changes():
                save_session_cache(session)



    else:

        profile, session, events, tracker_payload, field_timestamp_monitor = await compute_data(
            tracker_payload,
            tracker_config,
            source,
            console_log
        )

        # Update only when needed

        if profile and profile.has_not_saved_changes():
            save_profile_cache(profile)

        if session and session.has_not_saved_changes():
            save_session_cache(session)


    return profile, session, events, tracker_payload, field_timestamp_monitor
