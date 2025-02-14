from typing import Tuple, Optional, Union

from tracardi.domain.entity import PrimaryEntity, DefaultEntity, Entity
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.service.tracking.profile_loading import load_profile_and_session1
from tracardi.service.tracking.session_loading import load_or_create_session_1

from tracardi.domain.payload.tracker_payload import TrackerPayload


async def tracker_loading(tracker_payload: TrackerPayload,
                          is_static_profile_id: bool) -> Tuple[
    FlatProfile, Optional[Session], PrimaryEntity, Union[DefaultEntity, Entity]]:
    # We need profile and session before async

    flat_session = await load_or_create_session_1(*tracker_payload.for_session_creation())

    # -----------------------------------
    # Profile Loading

    flat_profile, session, tracker_profile, tracker_session = await load_profile_and_session1(
        flat_session,
        is_static_profile_id,
        tracker_payload.profile_less,
        tracker_payload.profile,
        tracker_payload.session
    )

    return flat_profile, session, tracker_profile, tracker_session
