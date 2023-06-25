import logging
import traceback
from typing import Type, Callable, Coroutine, Any, Optional

from tracardi.service.profile_merger import ProfileMerger

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.tracker_payloads import TrackerPayloads
from tracardi.domain.value_object.collect_result import CollectResult
from tracardi.exceptions.exception import UnauthorizedException
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.logger_manager import save_logs
from tracardi.service.setup.data.defaults import open_rest_source_bridge
from tracardi.service.storage.driver.elastic import profile as profile_db
from tracardi.service.storage.driver.elastic.operations import console_log as console_log_db
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

        result = await tr.track_event(tracker_payload)
        return result

    except Exception as e:
        traceback.print_exc()
        logger.error(str(e))
        raise e

    finally:
        # Save console log
        console_log_db.save_console_log(console_log)

        # Save log
        try:
            await save_logs()
        except Exception as e:
            logger.warning(f"Could not save logs. Error: {str(e)} ")


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
                source = await self.validate_source(tracker_payload)

                # Referencing profile by __tr_pid
                # ----------------------------------
                # Validate tracardi referer. Tracardi referer is a data that has profile_id, session_id. source_id.
                # It is used to keep the profile between jumps from domain to domain.

                # At this stage the profile and session are not loaded and are only Entities

                refer_source_id = tracker_payload.get_referer_data('source')
                if refer_source_id is not None and tracker_payload.has_referred_profile():
                    # If referred source is different then local web page source saved in JS script
                    try:
                        # Check if it is correct source. It will throw exception if incorrect
                        await self.check_source_id(refer_source_id)

                        referred_profile_id = tracker_payload.get_referer_data('profile')

                        # Check if profile id exists
                        profile_record = await profile_db.load_by_id(referred_profile_id)

                        if profile_record is not None:

                            # Profile will be replaced. Merge old profile to new one.

                            referred_profile = profile_record.to_entity(Profile)

                            # Merges referred profile in __tr_pid with profile existing in local storage on visited page
                            if tracker_payload.profile is not None:
                                # Merge profiles
                                merged_profile = await ProfileMerger.invoke_merge_profile(
                                    referred_profile,
                                    # Merge when id = tracker_payload.profile.id
                                    # This basically loads the current profile.
                                    merge_by=[('id', tracker_payload.profile.id)],
                                    limit=2000)
                                tracker_payload.profile = Entity(id=merged_profile.id)

                            else:
                                # Replace the profile in tracker payload with ref __tr_pid
                                tracker_payload.profile = Entity(id=referred_profile_id)

                            # Invalidate session. It may have wrong profile id
                            cache.session_cache().delete(tracker_payload.session.id)

                            # If no session create one
                            if tracker_payload.session is None:
                                tracker_payload.session = Session.new()

                        else:
                            logger.warning(f"Referred Tracardi Profile Id {referred_profile_id} is invalid.")

                    except ValueError as e:
                        logger.warning(f"Referred Tracardi Source Id {refer_source_id} is invalid. "
                                       f"The following error was returned {str(e)}.")

            # Update tracker source with full object
            tracker_payload.source = source

        except ValueError as e:
            raise UnauthorizedException(e)

        logger.debug(f"Source {source.id} validated.")

        # Run only for webhooks
        # Check if we need to generate profile and session id. Used in webhooks
        if tracker_payload.generate_profile_and_session_for_webhook(self.console_log):
            # Returns true if source is a webhook with generate profile id set to true
            self.tracker_config.static_profile_id = True

        # If REST API is configured to have static Profile ID
        if tracker_payload.source.config is not None and tracker_payload.source.config.get('static_profile_id', False):
            self.tracker_config.static_profile_id = True

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

    async def check_source_id(self, source_id) -> Optional[EventSource]:
        source = await cache.event_source(event_source_id=source_id, ttl=memory_cache.source_ttl)

        if source is not None:

            if not source.enabled:
                raise ValueError("Event source disabled.")

            if not source.is_allowed(self.tracker_config.allowed_bridges):
                raise ValueError(f"This endpoint allows only bridges of "
                                 f"types {self.tracker_config.allowed_bridges}, but the even source "
                                 f"`{source.name}`.`{source_id}` has types `{source.type}`. "
                                 f"Change bridge type in event source `{source.name}` to one that has endpoint type "
                                 f"{self.tracker_config.allowed_bridges} or call any `{source.type}` endpoint.")

        return source

    async def validate_source(self, tracker_payload: TrackerPayload) -> EventSource:

        source_id = tracker_payload.source.id
        ip = tracker_payload.metadata.ip

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

        source = await self.check_source_id(source_id)

        if source is None:
            raise ValueError(f"Invalid event source `{source_id}`. Request came from IP: `{ip}` "
                             f"width payload: {tracker_payload}")

        return source
