from typing import Tuple, Optional

from tracardi.domain.profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.service.tracking.profile_loading import load_profile_and_session
from tracardi.service.tracking.session_loading import load_or_create_session

from tracardi.domain.payload.tracker_payload import TrackerPayload

from tracardi.service.tracker_config import TrackerConfig


async def tracker_loading(tracker_payload: TrackerPayload,
                          tracker_config: TrackerConfig) -> Tuple[FlatProfile, Optional[Session]]:

    # We need profile and session before async

    session, tracker_payload = await load_or_create_session(tracker_payload)

    # -----------------------------------
    # Profile Loading

    flat_profile, session = await load_profile_and_session(
        session,
        tracker_config,
        tracker_payload
    )

    # TODO update finger print profile id

    return flat_profile, session
