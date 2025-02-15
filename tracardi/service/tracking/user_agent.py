from typing import Optional

from user_agents.parsers import UserAgent

from tracardi.domain.flat_session import FlatSession
from tracardi.domain.payload.tracker_payload import TrackerPayload


def _get_user_agent(flat_session: FlatSession, tracker_payload: TrackerPayload) -> Optional[UserAgent]:
    _user_agent = tracker_payload.get_user_agent()

    if _user_agent is not None:
        return _user_agent

    # Return user agent from session
    return flat_session.get_user_agent()