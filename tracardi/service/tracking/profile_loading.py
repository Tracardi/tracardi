from typing import Optional, Tuple

from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.session import Session
from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.flat_profile import FlatProfile

logger = get_logger(__name__)


async def load_profile_and_session(
        session: Session,
        is_static_profile_id: bool,
        tracker_payload: TrackerPayload
) -> Tuple[Optional[FlatProfile], Optional[Session]]:

    # Check if profile should have static ID

    if tracker_payload.profile_less is True:
        flat_profile = None
    else:
        flat_profile, session = await tracker_payload.get_profile_and_session(
            session,
            is_static_profile_id
        )

    # AT THIS POINT Profile is None only if is profile-less

    # Check if necessary hashed ID are present and add missing
    if flat_profile is not None:

        if flat_profile.hash_all_allowed_pii_as_ids():
            flat_profile.mark_for_update()

        # Add Ids from payload
        if isinstance(tracker_payload.profile, PrimaryEntity) and tracker_payload.profile.ids:
            payload_ids = set(tracker_payload.profile.ids)
            profile_ids = set(flat_profile.ids) if flat_profile.ids else set()
            payload_ids.update(profile_ids)
            # Check if update needed
            if profile_ids != payload_ids:
                # Something was added
                flat_profile.ids = list(payload_ids)
                flat_profile.mark_for_update()
                # TODO This may need to add changed fields and mark for merge but we do not know fields as ids are just numbers.

    return flat_profile, session
