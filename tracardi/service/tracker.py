import logging
import traceback
from typing import Type, Callable, Coroutine, Any

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.profile import Profile
from tracardi.domain.tracker_payloads import TrackerPayloads
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.exceptions.exception import UnauthorizedException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.logger_manager import save_logs
from tracardi.service.setup.data.defaults import open_rest_source_bridge
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
                      on_result_ready: Callable[
                          [List[TrackerResult], ConsoleLog], Coroutine[Any, Any, CollectResult]] = None
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

    except Exception as e:
        traceback.print_exc()
        logger.error(str(e))
        raise e

    finally:
        if await save_logs() is False:
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
            tracker_payload.source.id = str(tracker_payload.source.id).strip()
        if tracker_payload.session:
            tracker_payload.session.id = str(tracker_payload.session.id).strip()
        if tracker_payload.profile:
            tracker_payload.profile.id = str(tracker_payload.profile.id).strip()

        # Validate event source

        try:
            if self.tracker_config.internal_source is not None:
                if self.tracker_config.internal_source.id != tracker_payload.source.id:
                    msg = f"Invalid event source `{tracker_payload.source.id}`"
                    raise ValueError(msg)
                source = self.tracker_config.internal_source
            else:
                source = await self.validate_source(source_id=tracker_payload.source.id)

            # Update tracker source with full object
            tracker_payload.source = source

        except ValueError as e:
            raise UnauthorizedException(e)

        logger.debug(f"Source {source.id} validated.")

        # Check if we need to generate profile and session id. Used in webhooks
        tracker_payload.generate_profile_and_session()

        if self.on_source_ready is None:
            tp = TrackerProcessor(
                self.console_log,
                self.on_profile_merge,
                self.on_profile_ready,
                self.on_result_ready
            )

            return await tp.handle(
                TrackerPayloads([tracker_payload]),
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
            TrackerPayloads([tracker_payload]),
            source,
            self.tracker_config
        )

    async def validate_source(self, source_id: str) -> EventSource:

        if source_id == f"@{tracardi.fingerprint}":
            return EventSource(
                id=source_id,
                type=['rest'],
                bridge=NamedEntity(id=open_rest_source_bridge.id, name=open_rest_source_bridge.name),
                name="Internal event source",
                description="This is internal event source for internal events.",
                channel="Internal",
                transitional=False,  # ephemeral
                tags=['internal']
            )

        source = await cache.event_source(event_source_id=source_id, ttl=memory_cache.source_ttl)

        if source is None:
            raise ValueError(f"Invalid event source `{source_id}`")

        if not source.enabled:
            raise ValueError("Event source disabled.")

        if not source.is_allowed(self.tracker_config.allowed_bridges):
            raise ValueError(f"This endpoint allows only bridges of "
                             f"types {self.tracker_config.allowed_bridges}, but the even source "
                             f"`{source.name}`.`{source_id}` has types `{source.type}`. "
                             f"Change bridge type in event source `{source.name}` to one that has endpoint type "
                             f"{self.tracker_config.allowed_bridges} or call any `{source.type}` endpoint.")

        return source
