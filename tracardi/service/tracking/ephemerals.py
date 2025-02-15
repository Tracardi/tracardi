from typing import List, Tuple
from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.flat_session import FlatSession

logger = get_logger(__name__)


def remove_ephemeral_data(tracker_payload,
                          flat_profile: FlatProfile,
                          flat_session: FlatSession,
                          flat_events: List[FlatEvent]) -> Tuple[
    FlatProfile, FlatSession, List[FlatEvent]]:

    _save_session_flag = tracker_payload.is_on('saveSession', default=True)
    _save_events_flag = tracker_payload.is_on('saveEvents', default=True)
    _save_profile_flag = tracker_payload.is_on('saveProfile', default=True)

    if not _save_events_flag:
        flat_events = []

    if not _save_session_flag:
        flat_session = None
        for flat_event in flat_events:
            flat_event['session'] = None

    if not _save_profile_flag:
        flat_profile = None
        for flat_event in flat_events:
            flat_event['profile'] = None

    return flat_profile, flat_session, flat_events
