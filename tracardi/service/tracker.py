import time
from typing import Optional

from tracardi.domain.bridges.configurable_bridges import WebHookBridge, RestApiBridge, ConfigurableBridge
from tracardi.service.license import License
from tracardi.service.tracking.storage.profile_storage import load_profile
from tracardi.service.utils.date import now_in_utc
from tracardi.service.profile_merger import ProfileMerger
from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.session import Session
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.storage.mysql.bootstrap.bridge import open_rest_source_bridge
from tracardi.service.tracking.source_validation import validate_source
from tracardi.service.tracker_config import TrackerConfig
from tracardi.config import memory_cache, tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache_manager import CacheManager
from typing import List
if License.has_license():
    from com_tracardi.service.tracking.tracker import com_tracker
else:
    from tracardi.service.tracking.tracker import os_tracker

logger = get_logger(__name__)
cache = CacheManager()


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


class Tracker:

    def __init__(self, tracker_config: TrackerConfig):
        self.tracker_config = tracker_config

    async def _attach_referenced_profile(self, tracker_payload: TrackerPayload) -> TrackerPayload:
        refer_source_id = tracker_payload.get_referer_data('source')
        if refer_source_id is not None and tracker_payload.has_referred_profile():
            # If referred source is different then local web page source saved in JS script
            try:

                referred_profile_id = tracker_payload.get_referer_data('profile')

                # Referred profile ID is the same as tracker profile ID
                if tracker_payload.has_profile() and referred_profile_id == tracker_payload.profile.id:
                    return tracker_payload

                # Check again if it is correct source. It will throw exception if incorrect
                await self.check_source_id(refer_source_id)

                # Check if profile id exists

                # TODO should be in mutex
                # TODO ProfileMerger.invoke_merge_profile saves profile

                referred_profile = await load_profile(referred_profile_id)

                if referred_profile is not None:

                    # Profile will be replaced. Merge old profile to new one.
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
                        tracker_payload.session.profile = Entity(id=referred_profile_id)

                else:
                    logger.warning(f"Referred Tracardi Profile Id {referred_profile_id} is invalid.")

            except ValueError as e:
                logger.warning(f"Referred Tracardi Source Id {refer_source_id} is invalid. "
                               f"The following error was returned {str(e)}.")
        return tracker_payload

    @staticmethod
    def get_bridge(tracker_payload: TrackerPayload) -> Optional[ConfigurableBridge]:
        if not isinstance(tracker_payload.source, EventSource):
            logger.error("Can't configure bridge. Method get_bridge used before "
                         "EventSource was created.")

        if 'webhook' in tracker_payload.source.type:
            return WebHookBridge(
                id=tracker_payload.source.id,
                name=tracker_payload.source.name,
                config=tracker_payload.source.config
            )
        elif 'rest' in tracker_payload.source.type:
            return RestApiBridge(
                id=tracker_payload.source.id,
                name=tracker_payload.source.name,
                config=tracker_payload.source.config
            )

        return None

    async def track_event(self, tracker_payload: TrackerPayload, tracking_start: float):

        if tracker_payload.is_bot() and tracardi.disallow_bot_traffic:
            raise PermissionError(f"Traffic from bot is not allowed.")

            # Trim ids - spaces are frequent issues

        if tracker_payload.source:
            tracker_payload.source.id = str(tracker_payload.source.id).strip()
        if tracker_payload.session:
            tracker_payload.session.id = str(tracker_payload.session.id).strip()
        if tracker_payload.profile:
            tracker_payload.profile.id = str(tracker_payload.profile.id).strip()

        # Validate event source

        source = await validate_source(self.tracker_config, tracker_payload)

        logger.debug(f"Source {source.id} validated.")

        # Update tracker source with full event source object
        tracker_payload.source = source

        # Referencing profile by __tr_pid
        # ----------------------------------
        # Validate tracardi referer. Tracardi referer is a data that has profile_id, session_id. source_id.
        # It is used to keep the profile between jumps from domain to domain.

        # At this stage the profile and session are not loaded and are only Entities

        tracker_payload = await self._attach_referenced_profile(tracker_payload)

        # If there is a configurable bridge get it and set up tracker_payload and tracker_config

        configurable_bridge = self.get_bridge(tracker_payload)
        if configurable_bridge:
            tracker_payload, self.tracker_config = await configurable_bridge.configure(
                tracker_payload,
                self.tracker_config
            )

        # Is source ephemeral
        if tracker_payload.source.transitional is True:
            tracker_payload.set_ephemeral()

        if License.has_license():
            result = await com_tracker(
                source, tracker_payload,
                self.tracker_config, tracking_start
            )
        else:
            result = await os_tracker(
                source, tracker_payload,
                self.tracker_config, tracking_start
            )

        # if result and tracardi.enable_errors_on_response:
        #     result['errors'] += self.console_log.get_errors()
        #     result['warnings'] += self.console_log.get_warnings()

        return result

    async def check_source_id(self, source_id) -> Optional[EventSource]:

        if not tracardi.enable_event_source_check:
            return EventSource(
                id=source_id,
                type=['rest'],
                bridge=NamedEntity(id=open_rest_source_bridge.id, name=open_rest_source_bridge.name),
                name="Static event source",
                description="This event source is prepared because of ENABLE_EVENT_SOURCE_CHECK==no.",
                channel="Web",
                transitional=False,  # ephemeral
                timestamp=now_in_utc()
            )

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
