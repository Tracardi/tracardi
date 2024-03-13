from typing import Tuple, List, Optional


from tracardi.config import tracardi
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor
from tracardi.service.license import License
from tracardi.service.tracking.ephemerals import remove_ephemeral_data
from tracardi.service.tracking.event_data_computation import compute_events
from tracardi.service.tracking.profile_data_computation import update_profile_last_geo, update_profile_email_type, \
    update_profile_visits, update_profile_time, compute_profile_aux_geo_markets
from tracardi.service.tracking.session_data_computation import compute_session, update_device_geo, \
    update_session_utm_with_client_data
from tracardi.service.tracking.system_events import add_system_events

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload

from tracardi.service.tracker_config import TrackerConfig

if License.has_license():
    from com_tracardi.service.data_compliance import event_data_compliance
    from com_tracardi.service.identification_point_service import identify_and_merge_profile

async def _compute(source,
                   profile: Optional[Profile],
                   session: Optional[Session],
                   tracker_payload: TrackerPayload
                   ) -> Tuple[
    Optional[Profile], Optional[Session], List[Event], TrackerPayload, Optional[FieldTimestampMonitor]]:
    if profile is not None:

        if License.has_license():
            # Anonymize, data compliance

            event_payloads = await event_data_compliance(
                profile,
                event_payloads=tracker_payload.events)

            # Reassign events as there may be changes
            tracker_payload.events = event_payloads

            # Merge profile on identification points

            identification_points = await tracker_payload.list_identification_points()

            profile, event_payloads = await identify_and_merge_profile(profile,
                                                                       identification_points,
                                                                       tracker_payload.events)

            # Save event payload
            tracker_payload.events = event_payloads

        # Profile computation

        # Compute Profile GEO Markets and continent
        profile = compute_profile_aux_geo_markets(profile, session, tracker_payload)

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

    # Function compute_events also maps events to profile

    events, session, profile, field_timestamp_monitor = await compute_events(
        tracker_payload.events,  # All events with system events, and validation information
        tracker_payload.metadata,
        source,
        session,
        profile,  # Profile gets converted to FlatProfile
        tracker_payload.profile_less,
        tracker_payload
    )

    # Caution: After clear session can become None if set sessionSave = False

    return profile, session, events, tracker_payload, field_timestamp_monitor


async def compute_data(
        profile: Profile,
        session: Optional[Session],
        tracker_payload: TrackerPayload,
        tracker_config: TrackerConfig,
        source: EventSource) -> Tuple[
    Profile, Optional[Session], List[Event], TrackerPayload, Optional[FieldTimestampMonitor]]:

    # We need profile and session before async

    # ------------------------------------
    # Session computation

    if session:

        # Is new session
        if session.is_new():
            # Compute session. Session is filled only when new
            session = compute_session(
                session,
                tracker_payload,
                tracker_config
            )

        # Update missing data
        session = await update_device_geo(tracker_payload, session)
        session = update_session_utm_with_client_data(tracker_payload, session)

        # If agent is a bot stop
        if session.app.bot and tracardi.disallow_bot_traffic:
            raise PermissionError(f"Traffic from bot is not allowed.")

    profile, session, events, tracker_payload, field_timestamp_monitor = await _compute(
        source,
        profile,
        session,
        tracker_payload)

    # Removes data that should not be saved
    profile, session, events = remove_ephemeral_data(tracker_payload, profile, session, events)

    return profile, session, events, tracker_payload, field_timestamp_monitor
