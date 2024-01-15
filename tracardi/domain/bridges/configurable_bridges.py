import logging
from hashlib import md5
from typing import Optional, Tuple
from uuid import uuid4

from dotty_dict import Dotty

from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.config import memory_cache, tracardi
from tracardi.domain.profile_data import FLAT_PROFILE_FIELD_MAPPING
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.service.events import get_default_mappings_for
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.hasher import hash_id, uuid4_from_md5

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()

class ConfigurableBridge(NamedEntity):
    config: Optional[dict] = {}

    async def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig, console_log: ConsoleLog) -> Tuple[
        TrackerPayload, TrackerConfig, ConsoleLog]:
        pass


class WebHookBridge(ConfigurableBridge):

    @staticmethod
    async def _get_hashed_id(tracker_payload: TrackerPayload) -> Optional[str]:

        event = tracker_payload.events[0]
        flat_properties = Dotty({"properties": tracker_payload.events[0].properties})

        # Check if in custom event to profile mapping for current event type, there is a mapping for merging keys

        custom_event_to_profile_mapping = await cache.event_to_profile_coping(
            event_type=event.type,
            ttl=memory_cache.event_to_profile_coping_ttl)

        for item in custom_event_to_profile_mapping:
            custom_mapping_schema = item.to_entity(EventToProfile)
            for source, destination, _ in custom_mapping_schema.items():
                if source in flat_properties:
                    _merge_id = flat_properties[source]
                    _prefix = FLAT_PROFILE_FIELD_MAPPING[destination]
                    profile_id = hash_id(_merge_id, _prefix)
                    return profile_id

        # Check if in default event to profile mapping for current event type, there is a mapping for merging keys
        default_event_to_mapping_schema = get_default_mappings_for(event.type, 'copy')
        if default_event_to_mapping_schema is not None:

            for destination, source in default_event_to_mapping_schema.items():  # type: str, str
                if destination in FLAT_PROFILE_FIELD_MAPPING and source in flat_properties:
                    _merge_id = flat_properties[source]
                    _prefix = FLAT_PROFILE_FIELD_MAPPING[destination]
                    profile_id = hash_id(_merge_id, _prefix)
                    return profile_id

        return None

    async def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig, console_log: ConsoleLog) -> Tuple[
        TrackerPayload, TrackerConfig, ConsoleLog]:

        if self.config is not None:
            if 'generate_profile' in self.config:
                if self.config['generate_profile'] is True:

                    # Check if we can generate primary hashed ids
                    if tracardi.auto_profile_merging:
                        # Check if there can be a hashed id generated
                        profile_id = await self._get_hashed_id(tracker_payload)
                        if profile_id:
                            tracker_payload.replace_profile(profile_id)

                            sticky_session = self.config.get('sticky_session', True)

                            if sticky_session:
                                session_id = uuid4_from_md5(md5(f"{tracardi.auto_profile_merging}:{profile_id}".encode()).hexdigest())
                                tracker_payload.replace_session(session_id)

                    # Create random if does not exist

                    if not tracker_payload.session:
                        tracker_payload.replace_session(str(uuid4()))

                    if not tracker_payload.profile:
                        tracker_payload.replace_profile(str(uuid4()))



        return tracker_payload, tracker_config, console_log


class RestApiBridge(ConfigurableBridge):

    def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig, console_log: ConsoleLog) -> Tuple[
        TrackerPayload, TrackerConfig, ConsoleLog]:

        # If REST API is configured to have static Profile ID, set it in tracker config

        if tracker_payload.source.config is not None and tracker_payload.source.config.get('static_profile_id', False):
            tracker_config.static_profile_id = True

        return tracker_payload, tracker_config, console_log
