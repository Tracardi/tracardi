from typing import List, Tuple
from tracardi.exceptions.log_handler import get_logger
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session

logger = get_logger(__name__)


def remove_ephemeral_data(tracker_payload, profile: Profile, session: Session, events: List[Event]) -> Tuple[Profile, Session, List[Event]]:

    _save_session_flag = tracker_payload.is_on('saveSession', default=True)
    _save_events_flag = tracker_payload.is_on('saveEvents', default=True)
    _save_profile_flag = tracker_payload.is_on('saveProfile', default=True)

    logger.debug(f"Will Update: profile ({_save_profile_flag and bool(profile) and profile.has_not_saved_changes()}), "
                 f"session ({_save_session_flag and bool(session) and session.has_not_saved_changes()}), "
                 f"events({_save_events_flag and bool(events)})")

    if not _save_events_flag:
        events = []

    if not _save_session_flag:
        session = None
        for event in events:
            event.session = None

    if not _save_profile_flag:
        profile = None
        for event in events:
            event.profile = None

    return profile, session, events