import logging
from typing import Optional, Tuple

from tracardi.domain.console import Console
from tracardi.domain.session import Session
from tracardi.config import tracardi
from tracardi.exceptions.exception import DuplicatedRecordException
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.console_log import ConsoleLog
from tracardi.service.profile_deduplicator import deduplicate_profile
from tracardi.service.tracker_config import TrackerConfig
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.service.tracking.storage.profile_storage import load_profile

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def _load_profile_and_deduplicate(
        tracker_payload,
        is_static=False,
        console_log: Optional[ConsoleLog] = None
) -> Optional[Profile]:
    """
    Loads current profile. If profile was merged then it loads merged profile.
    @throws DuplicatedRecordException
    """
    if tracker_payload.profile is None:
        return None

    profile_id = tracker_payload.profile.id

    try:
        profile = await load_profile(profile_id)

        if profile is None:

            # Static profiles can be None as they need to be created if does not exist.
            # Static means the profile id was given in the track payload

            if is_static:
                profile = Profile(id=tracker_payload.profile.id)
                # This is new profile as we could not load it.
                profile.operation.new = True
                profile.operation.update = False
                return profile

            return None

        return profile

    except DuplicatedRecordException as e:

        message = (f"Profile duplication error. "
                   f"An error occurred when loading profile ID; {profile_id} "
                   f"Details: Profile {profile_id} needs deduplication. {repr(e)}")

        logger.warning(message)

        if isinstance(console_log, ConsoleLog):
            console_log.append(
                Console(
                    flow_id=None,
                    node_id=None,
                    event_id=None,
                    profile_id=profile_id,
                    origin='profile',
                    class_name='load_profile_and_deduplicate',
                    module=__name__,
                    type='warning',
                    message=message,
                    traceback=get_traceback(e)
                )
            )

        return await deduplicate_profile(profile_id)


async def load_profile_and_session(
        session: Session,
        tracker_config: TrackerConfig,
        tracker_payload: TrackerPayload,
        console_log: ConsoleLog
) -> Tuple[Optional[Profile], Optional[Session]]:

    # Load profile
    profile_loader = _load_profile_and_deduplicate

    # Force static profile id

    if tracker_config.static_profile_id is True or tracker_payload.has_static_profile_id():

        # Get static profile - This is dangerous
        profile, session = await tracker_payload.get_static_profile_and_session(
            session,
            profile_loader,  # Loads from memory if possible
            tracker_payload.profile_less,
            console_log
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
            tracker_payload.profile_less,
            console_log
        )

    return profile, session
