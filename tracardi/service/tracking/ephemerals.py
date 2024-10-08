from typing import List, Tuple
from tracardi.exceptions.log_handler import get_logger
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile, FlatProfile
from tracardi.domain.session import Session

logger = get_logger(__name__)


def remove_ephemeral_data(tracker_payload, flat_profile: FlatProfile, session: Session, events: List[Event]) -> Tuple[
    FlatProfile, Session, List[Event]]:

    _save_session_flag = tracker_payload.is_on('saveSession', default=True)
    _save_events_flag = tracker_payload.is_on('saveEvents', default=True)
    _save_profile_flag = tracker_payload.is_on('saveProfile', default=True)

    if not _save_events_flag:
        events = []

    if not _save_session_flag:
        session = None
        for event in events:
            event.session = None

    if not _save_profile_flag:
        flat_profile = None
        for event in events:
            event.profile = None

    return flat_profile, session, events
