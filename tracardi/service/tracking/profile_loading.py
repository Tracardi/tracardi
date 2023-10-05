import logging
from typing import Optional, Tuple

from tracardi.domain.session import Session
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.license import License
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.service.storage.driver.elastic import profile as profile_db

if License.has_license():
    from com_tracardi.service.identification_point_service import load_profile_and_deduplicate, \
        load_profile_deduplicate_and_identify


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def load_profile_and_session(session: Session,
                                   tracker_config: TrackerConfig,
                                   tracker_payload: TrackerPayload) -> Tuple[Optional[Profile], Optional[Session]]:
    # Load profile
    if License.has_license():
        profile_loader = load_profile_deduplicate_and_identify \
            if tracardi.enable_identification_point \
            else load_profile_and_deduplicate
    else:
        profile_loader = profile_db.load_profile_without_identification

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

    return profile, session
