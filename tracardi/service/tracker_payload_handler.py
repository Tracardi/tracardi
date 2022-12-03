from typing import Dict, List

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_persister import TrackerResultPersister
from tracardi.service.tracking_manager import TrackerResult
from tracardi.service.tracking_orchestrator import TrackingOrchestrator


async def handle_tracker_payloads(grouped_tracker_payloads: Dict[str, List[TrackerPayload]], attributes) -> List[CollectResult]:
    source, ip, run_async, static_profile_id = attributes

    """
    Starts collecting data and process it.
    """

    tracker_save_results = []
    for _, tracker_payloads in grouped_tracker_payloads.items():
        print("invoke", len(tracker_payloads))

        tracker_results: List[TrackerResult] = []
        console_log = ConsoleLog()

        orchestrator = TrackingOrchestrator(
            source,
            ip,
            console_log,
            run_async,
            static_profile_id
        )
        for tracker_payload in tracker_payloads:
            result = await orchestrator.invoke(tracker_payload)
            tracker_results.append(result)

        # Save bulk
        print("results", len(tracker_results))
        tp = TrackerResultPersister(console_log)
        save_results = await tp.persist(tracker_results)
        print(save_results)
        tracker_save_results.append(save_results)

    return tracker_save_results
