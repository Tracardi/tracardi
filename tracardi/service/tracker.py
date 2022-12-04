import logging
from typing import Callable, Any

import redis

from tracardi.exceptions.exception import UnauthorizedException, TracardiException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.storage.driver import storage
from tracardi.service.synchronizer import profile_synchronizer
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
        try:
            # Uses redis to lock profiles
            orchestrator = TrackingOrchestrator(source, tracker_config)

            for seq, (finger_print, tracker_payloads) in enumerate(grouped_tracker_payloads.items()):
                logger.info(f"Invoking {len(tracker_payloads)} tracker payloads.")

                console_log = ConsoleLog()
                tracker_results: List[TrackerResult] = []
                debugging: List[TrackerPayload] = []

                # Unlocks profile after context exit

                for tracker_payload in tracker_payloads:
                    # Locks for processing each profile
                    result = await orchestrator.invoke(tracker_payload, console_log)
                    tracker_results.append(result)
                    responses.append(result.get_response_body(tracker_payload.get_id()))
                    debugging.append(tracker_payload)

                # Save bulk

                if self.tracker_config.on_result_ready is None:
                    save_results = await self.handle_on_result_ready(tracker_results, console_log)
                else:
                    save_results = await self.tracker_config.on_result_ready(tracker_results, console_log)

                # print(save_results.profile)

                # UnLock

                if orchestrator.locked and source.synchronize_profiles:
                    profile_synchronizer.unlock_entities(orchestrator.locked)
                    await storage.driver.profile.refresh()
                    await storage.driver.session.refresh()

                logger.info(f"Invoke save results {save_results} tracker payloads.")

                # Debugging rest

                if tracardi.track_debug:
                    responses = save_results.get_debugging_info(responses, debugging)

        except redis.exceptions.ConnectionError as e:
            raise TracardiException(f"Could not connect to Redis server. Connection returned error {str(e)}")

        logger.info(f"Track responses {responses}.")
        if len(responses) == 1:
            return responses[0]
        return responses
