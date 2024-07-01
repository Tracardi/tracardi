import time
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.tracker import Tracker
from tracardi.service.tracker_config import TrackerConfig
from typing import List


async def track_event(tracker_payload: TrackerPayload,
                      ip: str,
                      allowed_bridges: List[str],
                      internal_source=None,
                      run_async: bool = False,
                      static_profile_id: bool = False
                      ):
    tracking_start = time.time()
    tr = Tracker(
        TrackerConfig(
            ip=ip,
            allowed_bridges=allowed_bridges,
            internal_source=internal_source,
            run_async=run_async,
            static_profile_id=static_profile_id
        )
    )

    return await tr.track_event(tracker_payload, tracking_start)
