import logging
from typing import Callable, Any
from tracardi.exceptions.exception import UnauthorizedException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.tracker_config import TrackerConfig
from tracardi.config import memory_cache, tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from typing import Dict, List
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_persister import TrackerResultPersister
from tracardi.service.tracking_manager import TrackerResult
from tracardi.service.tracking_orchestrator import TrackingOrchestrator

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


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
                      on_source_ready: Callable[[TrackerPayload, EventSource, 'TrackerConfig'], Any] = None,
                      on_profile_ready: Callable = None,
                      on_flow_ready: Callable = None,
                      on_result_ready: Callable = None,
                      internal_source=None,
                      run_async: bool = False,
                      static_profile_id: bool = False
                      ):
    tr = Tracker(
        TrackerConfig(
            ip=ip,
            allowed_bridges=allowed_bridges,
            on_source_ready=on_source_ready,
            on_profile_ready=on_profile_ready,
            on_flow_ready=on_flow_ready,
            on_result_ready=on_result_ready,
            internal_source=internal_source,
            run_async=run_async,
            static_profile_id=static_profile_id
        )
    )

    return await tr.track_event(tracker_payload)


class Tracker:

    def __init__(self, tracker_config: TrackerConfig):
        self.tracker_config = tracker_config

    async def track_event(self, tracker_payload: TrackerPayload):
        # Trim ids - spaces are frequent issues

        if tracker_payload.source:
            tracker_payload.source.id = tracker_payload.source.id.strip()
        if tracker_payload.session:
            tracker_payload.session.id = tracker_payload.session.id.strip()
        if tracker_payload.profile:
            tracker_payload.profile.id = tracker_payload.profile.id.strip()

        # Validate event source

        try:
            if self.tracker_config.internal_source is not None:
                if self.tracker_config.internal_source.id != tracker_payload.source.id:
                    raise ValueError(f"Invalid event source `{tracker_payload.source.id}`")
                source = self.tracker_config.internal_source
            else:
                source = await self.validate_source(source_id=tracker_payload.source.id)

        except ValueError as e:
            raise UnauthorizedException(e)

        if self.tracker_config.on_source_ready is None:
            return await self.handle_source_ready(
                {"no-finger-print": [tracker_payload]},
                source,
                self.tracker_config
            )

        # Custom handler

        return await self.tracker_config.on_source_ready(
            tracker_payload,
            source,
            self.tracker_config
        )

    async def validate_source(self, source_id: str) -> EventSource:
        source = await cache.event_source(event_source_id=source_id, ttl=memory_cache.source_ttl)

        if source is None:
            raise ValueError(f"Invalid event source `{source_id}`")

        if not source.enabled:
            raise ValueError("Event source disabled.")

        if source.type not in self.tracker_config.allowed_bridges:
            raise ValueError(f"Event source `{source_id}` is not within allowed bridge "
                             f"types {self.tracker_config.allowed_bridges}.")

        return source

    @staticmethod
    async def handle_on_result_ready(tracker_results, console_log) -> CollectResult:
        tp = TrackerResultPersister(console_log)
        return await tp.persist(tracker_results)

    async def handle_source_ready(self,
                                  grouped_tracker_payloads: Dict[str, List[TrackerPayload]],
                                  source: EventSource,
                                  tracker_config: TrackerConfig) -> List[CollectResult]:

        """
        Starts collecting data and process it.
        """
        responses = []
        for _, tracker_payloads in grouped_tracker_payloads.items():
            logger.info(f"Invoking {len(tracker_payloads)} tracker payloads.")

            console_log = ConsoleLog()
            tracker_results: List[TrackerResult] = []
            debugging: List[TrackerPayload] = []
            orchestrator = TrackingOrchestrator(
                source,
                tracker_config,
                console_log
            )
            for tracker_payload in tracker_payloads:
                result = await orchestrator.invoke(tracker_payload)
                tracker_results.append(result)
                responses.append(result.get_response_body())
                debugging.append(tracker_payload)

            # Save bulk
            if self.tracker_config.on_result_ready is None:
                save_results = await self.handle_on_result_ready(tracker_results, console_log)
            else:
                save_results = await self.tracker_config.on_result_ready(tracker_results, console_log)

            # Debugging rest
            # Debugging
            # if self.tracker_payload.is_debugging_on():
            if tracardi.track_debug:
                responses = save_results.get_debugging_info(responses, debugging)
                print(responses)
            # debug_result = TrackerPayloadResult(**collect_result.dict())
            #     debug_result = debug_result.dict()
            #     debug_result['execution'] = debugger
            #     debug_result['segmentation'] = segmentation_result
            #     debug_result['logs'] = console_log
            #     result['debugging'] = debug_result

            logger.info(f"Invoke save results {save_results} tracker payloads.")

        logger.info(f"Invoke responses {responses}.")
        if len(responses) == 1:
            return responses[0]
        return responses
