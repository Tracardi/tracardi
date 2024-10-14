from typing import Tuple, List, Optional

from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.service.change_monitoring.field_change_logger import FieldChangeLogger
from tracardi.service.tracking.ephemerals import remove_ephemeral_data
from tracardi.service.tracking.event_data_computation import compute_events
from tracardi.service.tracking.profile_data_computation import update_profile_last_geo, update_profile_email_type, \
    update_profile_visits, update_profile_time, compute_profile_aux_geo_markets
from tracardi.service.tracking.system_events import add_system_events

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload


async def _compute(source,
                   flat_profile: Optional[FlatProfile],
                   session: Optional[Session],
                   tracker_payload: TrackerPayload,
                   field_change_logger: FieldChangeLogger
                   ) -> Tuple[
    Optional[FlatProfile], Optional[Session], List[FlatEvent], TrackerPayload]:
    context = get_context()

    if flat_profile is not None:
        # Profile computation

        # Compute Profile GEO Markets and continent
        flat_profile, field_change_logger = compute_profile_aux_geo_markets(
            flat_profile, session, tracker_payload,field_change_logger)

        # Update profile last geo with session device geo
        flat_profile, field_change_logger = update_profile_last_geo(session, flat_profile, field_change_logger)

        # Update email type
        flat_profile, field_change_logger = update_profile_email_type(flat_profile, field_change_logger)

        # Update visits
        flat_profile, field_change_logger = update_profile_visits(session, flat_profile, field_change_logger)

        # Update profile time zone
        flat_profile, field_change_logger = update_profile_time(session, flat_profile, field_change_logger)

        context.profiler.measure('after-profile-computation')

        # Updates/Mutations of tracker_payload and session

        # Add system events
        if tracardi.system_events:
            tracker_payload, session = add_system_events(flat_profile.is_new(), session, tracker_payload)

    # ---------------------------------------------------------------------------
    # Compute events. Session can be changed if there is event e.g. visit-open
    # This should be last in the process. We need all data for event computation
    # events, session, profile = None, None, []
    # Profile has fields timestamps updated

    # Function compute_events also maps events to profile

    flat_events, session, flat_profile, field_change_logger = await compute_events(
        tracker_payload.events,  # All events with system events, and validation information
        tracker_payload.metadata,
        source,
        session,
        flat_profile,  # Profile gets converted to FlatProfile
        tracker_payload.profile_less,
        tracker_payload,
        field_change_logger
    )

    # Caution: After clear session can become None if set sessionSave = False

    return flat_profile, session, flat_events, tracker_payload


async def compute_data(
        flat_profile: Optional[FlatProfile],
        session: Optional[Session],
        tracker_payload: TrackerPayload,
        source: EventSource,
        field_change_logger: FieldChangeLogger) -> Tuple[
    Optional[FlatProfile], Optional[Session], List[FlatEvent], TrackerPayload]:
    # We need profile and session before async

    context = get_context()
    context.profiler.measure('after-profile-computation')

    flat_profile, session, flat_events, tracker_payload = await _compute(
        source,
        flat_profile,
        session,
        tracker_payload,
        field_change_logger)

    # Removes data that should not be saved
    flat_profile, session, flat_events = remove_ephemeral_data(tracker_payload, flat_profile, session, flat_events)

    return flat_profile, session, flat_events, tracker_payload
