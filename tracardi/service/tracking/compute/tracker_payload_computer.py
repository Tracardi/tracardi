from com_tracardi.service.data_compliance import event_data_compliance
from com_tracardi.service.tracking.event_validation import validate_events
from com_tracardi.service.tracking.tracker_event_reshaper import EventsReshaper
from tracardi.config import tracardi
from tracardi.domain.payload.tracker_payload import TrackerPayload


async def _anonymize_events(tracker_payload, profile):
    event_payloads = await event_data_compliance(
        profile,
        event_payloads=tracker_payload.events)

    # Reassign events as there may be changes
    tracker_payload.events = event_payloads

    return tracker_payload


async def compute_tracker_payload(tracker_payload: TrackerPayload, profile):
    # Validate events from tracker payload

    if tracardi.enable_event_validation:
        # CAUTION: Mutates the tracker payload and ads ProcessStatus to events.
        # Validate events. Checks validators and its conditions and sets validation status.
        # Event payload will be filled with validation status. Mutates tracker_payload
        tracker_payload = await validate_events(tracker_payload)

    if tracardi.enable_event_reshaping:
        # Reshape valid events
        # CAUTION: Mutates the tracker payload
        evh = EventsReshaper(tracker_payload)
        tracker_payload = await evh.reshape_events()

    # Anonymize, data compliance
    tracker_payload = await _anonymize_events(tracker_payload, profile)

    return tracker_payload
