from typing import Tuple, Optional

from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.service.tracking.profile_loading import load_profile_and_session
from tracardi.service.tracking.session_loading import load_or_create_session_1

from tracardi.domain.payload.tracker_payload import TrackerPayload



async def tracker_loading(tracker_payload: TrackerPayload,
                          is_static_profile_id: bool) -> Tuple[FlatProfile, Optional[Session]]:

    # We need profile and session before async

    session, tracker_payload = await load_or_create_session_1(*tracker_payload.for_session_creation())

    # -----------------------------------
    # Profile Loading

    flat_profile, session = await load_profile_and_session(
        session,
        is_static_profile_id,
        tracker_payload
    )

    # TODO update finger print profile id

    return flat_profile, session
