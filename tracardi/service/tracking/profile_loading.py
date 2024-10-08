from typing import Optional, Tuple

from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile, FlatProfile

logger = get_logger(__name__)


async def load_profile_and_session(
        session: Session,
        tracker_config: TrackerConfig,
        tracker_payload: TrackerPayload
) -> Tuple[Optional[FlatProfile], Optional[Session]]:

    # Check if profile should have static ID

    is_static = tracker_config.static_profile_id is True or tracker_payload.has_static_profile_id()

    flat_profile, session = await tracker_payload.get_profile_and_session(
        session,
        is_static,
        tracker_payload.profile_less
    )

    # AT THIS POINT Profile is None only if is profile-less

    # Check if necessary hashed ID are present and add missing
    if flat_profile is not None:

        changed_fields = flat_profile.create_auto_merge_hashed_ids()
        if changed_fields:
            flat_profile.mark_for_update()
            flat_profile.metadata.system.set_auto_merge_fields(changed_fields)
        # Removed not needed to always hash IDS. Hash only on update.
        # Mark profile if the hashed IDs can be computed on its PII.
        # event_types = tracker_payload.get_event_types()
        # if can_profile_pii_be_hashed_in_ids(event_types):
        #     has_changes = flat_profile.hash_all_allowed_pii_as_ids()
        #     if has_changes:
        #         flat_profile.mark_for_update()

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
