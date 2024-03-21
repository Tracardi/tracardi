import time
from typing import List
from tracardi.service.tracker import Tracker
from tracardi.service.tracker_config import TrackerConfig
from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.log_handler import get_logger


logger = get_logger(__name__)

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




async def exec_send_event(tracker_payload: TrackerPayload, bridge_type: List[str]):
    tracker_payload.set_ephemeral(False)

    logger.debug(f"Resuming workflow in {get_context()} with {tracker_payload.options}")
    logger.debug(f"Accepted internal source is {tracardi.internal_source}.")

    # Must be here as it is a dynamic send and makes circular reference

    await track_event(
        tracker_payload,
        ip="0.0.0.0",
        allowed_bridges=bridge_type,
        static_profile_id=True
    )