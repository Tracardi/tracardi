from typing import List

from tracardi.config import tracardi


def can_profile_pii_be_hashed_in_ids(tracked_event_types: List[str]) -> bool:
    """
    Defines a logic when the PII hashing as IDS is available.
    """

    if not tracardi.is_apm_on():
        return False

    if tracardi.has_defined_identification_event_type():
        # Check if the event type exists in tracker payload.
        return tracardi.identification_event_type in tracked_event_types
    else:
        # Available for all event types as default
        return True


def get_allowed_piis_to_be_hashed_as_ids() -> list[str]:
    if not tracardi.identification_event_property:
        return []

    return tracardi.identification_event_property.split(',')
