from tracardi.service.tracking.cache.profile_cache import save_profile_cache
from tracardi.service.tracking.cache.session_cache import save_session_cache
from tracardi.service.tracking.event_data_computation import compute_events
from tracardi.service.tracking.profile_data_computation import update_profile_last_geo, update_profile_email_type, \
    update_profile_visits, update_profile_time
from tracardi.service.tracking.session_data_computation import compute_session, update_device_geo, \
    update_session_utm_with_client_data
from tracardi.service.tracking.profile_loading import load_profile_and_session
from tracardi.service.tracking.session_loading import load_or_create_session
from tracardi.service.tracking.tracker_persister_async import clear_relations

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload

from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_config import TrackerConfig


async def compute_data(tracker_payload: TrackerPayload,
                       tracker_config: TrackerConfig,
                       source: EventSource,
                       console_log: ConsoleLog):

    # We need profile and session before async

    session, tracker_payload = await load_or_create_session(tracker_payload)

    # Load profile

    profile, session = await load_profile_and_session(
        session,
        tracker_config,
        tracker_payload,
        console_log
    )

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

    # ---------------------------------------------------------------------------
    # Compute events. Session can be changed if there is event e.g. visit-open
    # This should be last in the process. We need all data for event computation
    # events, session, profile = None, None, []

    events, session, profile = await compute_events(
        tracker_payload.events,  # All events with system events, and validation information
        tracker_payload.metadata,
        source,
        session,
        profile,
        tracker_payload.profile_less,
        console_log,
        tracker_payload
    )

    profile, session, events = clear_relations(tracker_payload, profile, session, events)

    # Cache recent profile and session changes

    print("----------------------------------------")
    print(profile.id, "metadata", profile.get_meta_data())
    print(profile.id, "new profile", profile.operation)

    return profile, session, events, tracker_payload
