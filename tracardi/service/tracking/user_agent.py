from typing import Optional

from user_agents.parsers import UserAgent

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.session import Session


def _get_user_agent(session: Session, tracker_payload: TrackerPayload) -> Optional[UserAgent]:
    _user_agent = tracker_payload.get_user_agent()

    if _user_agent is not None:
        return _user_agent

    # Return user agent from session
    return session.get_user_agent()