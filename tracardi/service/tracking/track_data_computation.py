from typing import Tuple, List, Optional

from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.change_monitoring.field_change_logger import FieldChangeLogger
from tracardi.service.license import License
from tracardi.service.tracking.ephemerals import remove_ephemeral_data
from tracardi.service.tracking.event_data_computation import compute_events
from tracardi.service.tracking.profile_data_computation import update_profile_last_geo, update_profile_email_type, \
    update_profile_visits, update_profile_time, compute_profile_aux_geo_markets
from tracardi.service.tracking.system_events import add_system_events

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload

if License.has_license():
    from com_tracardi.service.identification_point_service import identify_and_merge_profile


async def _compute(source,
                   profile: Optional[Profile],
                   session: Optional[Session],
                   tracker_payload: TrackerPayload,
                   field_change_logger: FieldChangeLogger
                   ) -> Tuple[
    Optional[Profile], Optional[Session], List[Event], TrackerPayload]:
    context = get_context()

    if profile is not None:

        if License.has_license():

            # Merge profile on identification points

            identification_points = await tracker_payload.list_identification_points()

            profile = await identify_and_merge_profile(profile,
                                                       identification_points,
                                                       tracker_payload.events)

        # Profile computation

        # Compute Profile GEO Markets and continent
        profile, field_change_logger = compute_profile_aux_geo_markets(profile, session, tracker_payload,
                                                                       field_change_logger)

        # Update profile last geo with session device geo
        profile, field_change_logger = update_profile_last_geo(session, profile, field_change_logger)

        # Update email type
        profile, field_change_logger = update_profile_email_type(profile, field_change_logger)

        # Update visits
        profile, field_change_logger = update_profile_visits(session, profile, field_change_logger)

        # Update profile time zone
        profile, field_change_logger = update_profile_time(session, profile, field_change_logger)

        context.profiler.measure('after-profile-computation')

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

    events, session, profile, field_change_logger = await compute_events(
        tracker_payload.events,  # All events with system events, and validation information
        tracker_payload.metadata,
        source,
        session,
        profile,  # Profile gets converted to FlatProfile
        tracker_payload.profile_less,
        tracker_payload,
        field_change_logger
    )

    # Caution: After clear session can become None if set sessionSave = False

    return profile, session, events, tracker_payload


async def compute_data(
        profile: Profile,
        session: Optional[Session],
        tracker_payload: TrackerPayload,
        source: EventSource,
        field_change_logger: FieldChangeLogger) -> Tuple[
    Profile, Optional[Session], List[Event], TrackerPayload]:
    # We need profile and session before async

    context = get_context()
    context.profiler.measure('after-profile-computation')

    profile, session, events, tracker_payload = await _compute(
        source,
        profile,
        session,
        tracker_payload,
        field_change_logger)

    # Removes data that should not be saved
    profile, session, events = remove_ephemeral_data(tracker_payload, profile, session, events)

    return profile, session, events, tracker_payload
