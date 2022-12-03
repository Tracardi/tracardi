import logging
from typing import List, Callable
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.exceptions.exception import UnauthorizedException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.storage.helpers.source_cacher import validate_source
from tracardi.service.tracker_payload_handler import handle_tracker_payloads


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


# Todo remove 2023-04-01 - obsolete
async def synchronized_event_tracking(tracker_payload: TrackerPayload, host: str, profile_less: bool,
                                      allowed_bridges: List[str], internal_source=None):
    tracker_payload.profile_less = profile_less
    return await track_event(tracker_payload,
                             ip=host,
                             allowed_bridges=allowed_bridges,
                             internal_source=internal_source)


async def track_event(tracker_payload: TrackerPayload,
                      ip: str,
                      allowed_bridges: List[str],
                      on_ready: Callable = None,
                      internal_source=None,
                      run_async: bool = False,
                      static_profile_id: bool = False
                      ):
    # Trim ids - spaces are frequent issues

    if tracker_payload.source:
        tracker_payload.source.id = tracker_payload.source.id.strip()
    if tracker_payload.session:
        tracker_payload.session.id = tracker_payload.session.id.strip()
    if tracker_payload.profile:
        tracker_payload.profile.id = tracker_payload.profile.id.strip()

    # Validate event source

    try:
        if internal_source is not None:
            if internal_source.id != tracker_payload.source.id:
                raise ValueError(f"Invalid event source `{tracker_payload.source.id}`")
            source = internal_source
        else:
            source = await validate_source(
                source_id=tracker_payload.source.id,
                allowed_bridges=allowed_bridges)

    except ValueError as e:
        raise UnauthorizedException(e)

    if on_ready is None:
        return await handle_tracker_payloads(
            {"no-finger-print": [tracker_payload]},
            (source, ip, run_async, static_profile_id)
        )

    # Custom handler

    return await on_ready(
        tracker_payload,
        (source, ip, run_async, static_profile_id)
    )

