from typing import Tuple, List, Optional

from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.service.tracking.ephemerals import remove_ephemeral_data
from tracardi.service.tracking.event_data_computation import compute_events
from tracardi.service.tracking.profile_data_computation import update_profile_last_geo, update_profile_email_type, \
    update_profile_visits, update_profile_time, compute_profile_aux_geo_markets
from tracardi.service.tracking.system_events import add_system_events

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload

def _compute_profile_properties(flat_profile, session):
    # Compute Profile GEO Markets and continent
    yield from compute_profile_aux_geo_markets(flat_profile, session.context)

    # Update profile last geo with session device geo
    yield from update_profile_last_geo(flat_profile, session.context)

    # Update email type
    yield from update_profile_email_type(flat_profile)

    # Update visits
    yield from update_profile_visits(session.is_new(), flat_profile)

    # Update profile time zone
    yield from update_profile_time(flat_profile, session.context)


async def _compute(source,
                   flat_profile: Optional[FlatProfile],
                   session: Optional[Session],
                   tracker_payload: TrackerPayload
                   ) -> Tuple[
    Optional[FlatProfile], Optional[Session], List[FlatEvent], TrackerPayload]:
    context = get_context()

    if flat_profile is not None:
        # Profile computation

        for field_change in _compute_profile_properties(flat_profile, session):
            flat_profile.set(field_change.field, field_change.value, session_id=session.id)

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

    flat_events, session, flat_profile = await compute_events(
        tracker_payload.events,  # All events with system events, and validation information
        tracker_payload.metadata,
        source,
        session,
        flat_profile,  # Profile gets converted to FlatProfile
        tracker_payload.profile_less,
        tracker_payload
    )

    print(1, flat_profile.has_not_saved_changes())
    print(2, flat_profile.has_changes())

    # Caution: After clear session can become None if set sessionSave = False

    return flat_profile, session, flat_events, tracker_payload


async def compute_data(
        flat_profile: Optional[FlatProfile],
        session: Optional[Session],
        tracker_payload: TrackerPayload,
        source: EventSource) -> Tuple[
    Optional[FlatProfile], Optional[Session], List[FlatEvent], TrackerPayload]:
    # We need profile and session before async

    context = get_context()
    context.profiler.measure('after-profile-computation')

    flat_profile, session, flat_events, tracker_payload = await _compute(
        source,
        flat_profile,
        session,
        tracker_payload)

    # Removes data that should not be saved
    flat_profile, session, flat_events = remove_ephemeral_data(tracker_payload, flat_profile, session, flat_events)

    return flat_profile, session, flat_events, tracker_payload
