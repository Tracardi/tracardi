import asyncio
import logging
from typing import Type, Callable, Coroutine, Any

from tracardi.domain.profile import Profile
from tracardi.domain.tracker_payloads import TrackerPayloads
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.exceptions.exception import UnauthorizedException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.storage.driver import storage
from tracardi.service.tracker_config import TrackerConfig
from tracardi.config import memory_cache, tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from typing import List
from tracardi.service.console_log import ConsoleLog
from tracardi.service.tracker_processor import TrackerProcessor, TrackProcessorBase
from tracardi.service.tracking_manager import TrackingManagerBase, TrackerResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()


async def track_event(tracker_payload: TrackerPayload,
                      ip: str,
                      allowed_bridges: List[str],
                      internal_source=None,
                      run_async: bool = False,
                      static_profile_id: bool = False,
                      on_source_ready: Type[TrackProcessorBase] = None,
                      on_profile_merge: Callable[[Profile], Profile] = None,
                      on_profile_ready: Type[TrackingManagerBase] = None,
                      on_result_ready: Callable[[List[TrackerResult], ConsoleLog], Coroutine[Any, Any, CollectResult]] = None
                      ):

    console_log = ConsoleLog()
    try:

        tr = Tracker(
            console_log,
            TrackerConfig(
                ip=ip,
                allowed_bridges=allowed_bridges,
                internal_source=internal_source,
                run_async=run_async,
                static_profile_id=static_profile_id
            ),
            on_source_ready=on_source_ready,
            on_profile_merge=on_profile_merge,
            on_profile_ready=on_profile_ready,
            on_result_ready=on_result_ready
        )

        return await tr.track_event(tracker_payload)

    finally:
        if tracardi.save_logs:
            """
            Saves errors caught by logger
            """
            if await storage.driver.log.exists():
                if log_handler.has_logs():
                    # do not await
                    asyncio.create_task(storage.driver.log.save(log_handler.collection))
                    log_handler.reset()
            else:
                logger.warning("Log index still not created. Saving logs postponed.")


class Tracker:

    def __init__(self,
                 console_log: ConsoleLog,
                 tracker_config: TrackerConfig,
                 on_source_ready: Type[TrackProcessorBase] = None,
                 on_profile_merge: Callable[[Profile], Profile] = None,
                 on_profile_ready: Type[TrackingManagerBase] = None,
                 on_result_ready: Callable[[List[TrackerResult], ConsoleLog], Coroutine[Any, Any, CollectResult]] = None
                 ):

        self.on_source_ready = on_source_ready
        self.on_result_ready = on_result_ready
        self.on_profile_ready = on_profile_ready
        self.on_profile_merge = on_profile_merge
        self.console_log = console_log
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

            # Update tracker source with full object
            tracker_payload.source = source

        except ValueError as e:
            raise UnauthorizedException(e)

        if self.on_source_ready is None:

            tp = TrackerProcessor(
                self.console_log,
                self.on_profile_merge,
                self.on_profile_ready,
                self.on_result_ready
            )

            return await tp.handle(
                TrackerPayloads({"no-finger-print": [tracker_payload]}),
                source,
                self.tracker_config
            )

        # Custom handler
        if not issubclass(self.on_source_ready, TrackProcessorBase):
            raise AssertionError("Callable self.tracker_config.on_source_ready must a TrackProcessorBase object.")

        tp = self.on_source_ready(
            self.console_log,
            self.on_profile_merge,
            self.on_profile_ready,
            self.on_result_ready
        )
        return await tp.handle(
            TrackerPayloads({"no-finger-print": [tracker_payload]}),  ## todo ? TrackerPayload may have fingerprints, I do not know
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
