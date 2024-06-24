from typing import Optional, Tuple

from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.service.tracking.storage.profile_storage import load_profile

logger = get_logger(__name__)


async def _load_profile_and_deduplicate(
        tracker_payload,
        is_static=False) -> Optional[Profile]:
    """
    Loads current profile. If profile was merged then it loads merged profile.
    """
    if tracker_payload.profile is None:
        return None

    profile_id = tracker_payload.profile.id

    profile = await load_profile(profile_id)

    if profile is not None:
        return profile

    if not is_static:
        return None

    # Static profiles can be None as they need to be created if does not exist.
    # Static means the profile id was given in the track payload

    profile = tracker_payload.create_default_profile()
    # This is new profile as we could not load it.
    profile.set_new()
    profile.set_updated(False)
    return profile


async def load_profile_and_session(
        session: Session,
        tracker_config: TrackerConfig,
        tracker_payload: TrackerPayload
) -> Tuple[Optional[Profile], Optional[Session]]:
    # Load profile
    profile_loader = _load_profile_and_deduplicate

    # Force static profile id

    if tracker_config.static_profile_id is True or tracker_payload.has_static_profile_id():

        # Get static profile - This is dangerous
        profile, session = await tracker_payload.get_static_profile_and_session(
            session,
            profile_loader,  # Loads from memory if possible
            tracker_payload.profile_less
        )

        # Profile exists but was merged
        if profile is not None and profile.is_merged(tracker_payload.profile.id):
            _forced_events = [ev.type for ev in tracker_payload.events]
            err_msg = f"Profile ID {tracker_payload.profile.id} was merged with {profile.id}, " \
                      f"but the old ID {tracker_payload.profile.id} was forced to be used. " \
                      f" As a result, events of type {_forced_events} will continue to be saved using the old " \
                      "profile ID. This is acceptable for the 'visit-ended' event type since it ensures the " \
                      "closure of the previous profile visit. However, for other event types, it may suggest " \
                      "that the client failed to switch or update the profile ID appropriately."
            if 'visit-ended' in _forced_events:
                logger.info(err_msg)
            else:
                logger.warning(err_msg)
            profile.id = tracker_payload.profile.id
    else:
        profile, session = await tracker_payload.get_profile_and_session(
            session,
            profile_loader,  # Loads from memory if possible
            tracker_payload.profile_less
        )

    # Check if necessary hashed ID are present and add missing
    if profile is not None:

        changed_fields = profile.create_auto_merge_hashed_ids()
        if changed_fields:
            profile.mark_for_update()
            profile.metadata.system.set_auto_merge_fields(changed_fields)

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
