import asyncio
import logging
from typing import List, Dict
from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from tracardi.exceptions.exception import UnauthorizedException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.console_log import ConsoleLog
from tracardi.service.pool_manager import PoolManager
from tracardi.service.storage.helpers.source_cacher import validate_source
from tracardi.service.tracker_persister import TrackerResultPersister
from tracardi.service.tracking_manager import TrackerResult
from tracardi.service.tracking_orchestrator import TrackingOrchestrator

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def send_data(grouped_tracker_payloads: Dict[str, List[TrackerPayload]], attributes):
    source, ip, run_async, static_profile_id = attributes

    tracker_save_results = []
    for finger_print, tracker_payloads in grouped_tracker_payloads.items():
        print("invoke", len(tracker_payloads))

        tracker_results: List[TrackerResult] = []
        console_log = ConsoleLog()

        for tracker_payload in tracker_payloads:
            orchestrator = TrackingOrchestrator(
                tracker_payload,
                source,
                ip,
                console_log,
                run_async,
                static_profile_id
            )
            result = await orchestrator.invoke()
            tracker_results.append(result)

        # Save bulk
        print("results", len(tracker_results))
        tp = TrackerResultPersister(console_log)
        save_results = await tp.persist(tracker_results)
        print(save_results)
        tracker_save_results.append(save_results)
    return tracker_save_results

pool = PoolManager('event-pooling',
                   max_pool=10,
                   pass_pool_as_dict=True,
                   on_pool_purge=send_data)


async def track_event(tracker_payload: TrackerPayload,
                      ip: str,
                      allowed_bridges: List[str],
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

    # Async
    pool.set_ttl(asyncio.get_running_loop(), ttl=3)
    pool.set_attributes(
        (source, ip, run_async, static_profile_id)
    )

    # If async
    await pool.append(tracker_payload, key=tracker_payload.get_finger_print())

    # No async

    # Todo no return right now

    # tracker_result = await invoke_track_process_step_0(
    #     [tracker_payload],
    #     source,
    #     ip,
    #     run_async,
    #     static_profile_id
    # )


# Todo remove 2023-04-01 - obsolete
async def synchronized_event_tracking(tracker_payload: TrackerPayload, host: str, profile_less: bool,
                                      allowed_bridges: List[str], internal_source=None):
    tracker_payload.profile_less = profile_less
    return await track_event(tracker_payload,
                             ip=host,
                             allowed_bridges=allowed_bridges,
                             internal_source=internal_source)
