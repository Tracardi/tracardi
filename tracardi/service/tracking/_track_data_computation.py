# from typing import Tuple, List, Optional
#
# from tracardi.config import tracardi
# from tracardi.context import get_context
# from tracardi.domain.flat_event import FlatEvent
# from tracardi.domain.flat_profile import FlatProfile
# from tracardi.domain.flat_session import FlatSession
# from tracardi.service.tracking.ephemerals import remove_ephemeral_data
# from tracardi.service.tracking.event_data_computation import compute_events
# from tracardi.service.tracking.profile_data_computation import update_profile_last_geo, update_profile_email_type, \
#     update_profile_visits, update_profile_time, compute_profile_aux_geo_markets
# from tracardi.service.tracking.system_events import add_system_events
#
# from tracardi.domain.event_source import EventSource
# from tracardi.domain.payload.tracker_payload import TrackerPayload
#
# def _compute_profile_properties(flat_profile, flat_session: FlatSession):
#     # Compute Profile GEO Markets and continent
#     yield from compute_profile_aux_geo_markets(flat_profile, flat_session['context'])
#
#     # Update profile last geo with session device geo
#     yield from update_profile_last_geo(flat_profile, flat_session['context'])
#
#     # Update email type
#     yield from update_profile_email_type(flat_profile)
#
#     # Update visits
#     yield from update_profile_visits(flat_session.is_new(), flat_profile)
#
#     # Update profile time zone
#     yield from update_profile_time(flat_profile, flat_session['context'])
#
#
# async def _compute(source,
#                    flat_profile: Optional[FlatProfile],
#                    flat_session: Optional[FlatSession],
#                    tracker_payload: TrackerPayload
#                    ) -> Tuple[
#     Optional[FlatProfile], Optional[FlatSession], List[FlatEvent], TrackerPayload]:
#     context = get_context()
#
#     if flat_profile is not None:
#         # Profile computation
#
#         for field_change in _compute_profile_properties(flat_profile, flat_session):
#             flat_profile.set(field_change.field, field_change.value, session_id=flat_session.id, timestamp=field_change.ts)
#
#         context.profiler.measure('after-profile-computation')
#
#         # Updates/Mutations of tracker_payload and session
#
#         # Add system events
#         if tracardi.system_events:
#             tracker_payload, flat_session = add_system_events(flat_session, tracker_payload)
#
#     # ---------------------------------------------------------------------------
#     # Compute events. Session can be changed if there is event e.g. visit-open
#     # This should be last in the process. We need all data for event computation
#     # events, session, profile = None, None, []
#     # Profile has fields timestamps updated
#
#     # Function compute_events also maps events to profile
#
#     flat_events, flat_session, flat_profile = await compute_events(
#         tracker_payload.events,  # All events with system events, and validation information
#         tracker_payload.metadata,
#         source,
#         flat_session,
#         flat_profile,  # Profile gets converted to FlatProfile
#         tracker_payload.profile_less,
#         tracker_payload
#     )
#
#     # Caution: After clear session can become None if set sessionSave = False
#
#     return flat_profile, flat_session, flat_events, tracker_payload
#
#
# async def compute_data(
#         flat_profile: Optional[FlatProfile],
#         flat_session: Optional[FlatSession],
#         tracker_payload: TrackerPayload,
#         source: EventSource) -> Tuple[
#     Optional[FlatProfile], Optional[FlatSession], List[FlatEvent], TrackerPayload]:
#     # We need profile and session before async
#
#     context = get_context()
#     context.profiler.measure('after-profile-computation')
#
#     flat_profile, flat_session, flat_events, tracker_payload = await _compute(
#         source,
#         flat_profile,
#         flat_session,
#         tracker_payload)
#
#     # Removes data that should not be saved
#     flat_profile, flat_session, flat_events = remove_ephemeral_data(tracker_payload, flat_profile, flat_session, flat_events)
#
#     return flat_profile, flat_session, flat_events, tracker_payload
