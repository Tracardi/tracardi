from typing import Optional, Tuple

from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile

logger = get_logger(__name__)


async def load_profile_and_session(
        session: Session,
        tracker_config: TrackerConfig,
        tracker_payload: TrackerPayload
) -> Tuple[Optional[Profile], Optional[Session]]:

    # Check if profile should have static ID

    is_static = tracker_config.static_profile_id is True or tracker_payload.has_static_profile_id()

    profile, session = await tracker_payload.get_profile_and_session(
        session,
        is_static,
        tracker_payload.profile_less
    )

    # AT THIS POINT Profile is None only if is profile-less

    # Check if necessary hashed ID are present and add missing
    if profile is not None:

        # Removed not needed to always hash IDS. Hash only on update.
        # Mark profile if the hashed IDs can be computed on its PII.
        # event_types = tracker_payload.get_event_types()
        # if can_profile_pii_be_hashed_in_ids(event_types):
        #     has_changes = profile.hash_all_allowed_pii_as_ids()
        #     if has_changes:
        #         profile.mark_for_update()

        # Add Ids from payload
        if isinstance(tracker_payload.profile, PrimaryEntity) and tracker_payload.profile.ids:
            payload_ids = set(tracker_payload.profile.ids)
            profile_ids = set(profile.ids) if profile.ids else set()
            payload_ids.update(profile_ids)
            # Check if update needed
            if profile_ids != payload_ids:
                # Something was added
                profile.ids = list(payload_ids)
                profile.mark_for_update()
                # TODO This may need to add changed fields and mark for merge but we do not know fields as ids are just numbers.

    return profile, session
