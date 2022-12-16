import logging
import redis

from abc import ABC, abstractmethod
from tracardi.exceptions.exception import TracardiException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.storage.driver import storage
from tracardi.service.synchronizer import profile_synchronizer
from tracardi.service.tracker_config import TrackerConfig
from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from typing import Dict, List
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_persister import TrackerResultPersister
from tracardi.service.tracking_manager import TrackerResult
from tracardi.service.tracking_orchestrator import TrackingOrchestrator

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class TrackProcessorBase(ABC):

    def __init__(self, console_log: ConsoleLog, tracker_config: TrackerConfig):
        self.console_log = console_log
        self.tracker_config = tracker_config

    @abstractmethod
    async def _handle_on_result_ready(self, tracker_results) -> CollectResult:
        pass

    @abstractmethod
    async def handle(self,
                     grouped_tracker_payloads: Dict[str, List[TrackerPayload]],
                     source: EventSource,
                     tracker_config: TrackerConfig) -> List[CollectResult]:
        pass


class TrackerProcessor(TrackProcessorBase):

    async def _handle_on_result_ready(self, tracker_results) -> CollectResult:
        tp = TrackerResultPersister(self.console_log)
        return await tp.persist(tracker_results)

    async def handle(self,
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

                tracker_results: List[TrackerResult] = []
                debugging: List[TrackerPayload] = []

                # Unlocks profile after context exit

                for tracker_payload in tracker_payloads:
                    # Locks for processing each profile
                    result = await orchestrator.invoke(tracker_payload, self.console_log)
                    tracker_results.append(result)
                    responses.append(result.get_response_body(tracker_payload.get_id()))
                    debugging.append(tracker_payload)

                # Save bulk

                if self.tracker_config.on_result_ready is None:
                    save_results = await self._handle_on_result_ready(tracker_results)
                else:
                    save_results = await self.tracker_config.on_result_ready(tracker_results, self.console_log)

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
