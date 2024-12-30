from hashlib import md5
from typing import Optional, Tuple, List
from uuid import uuid4

from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.config import tracardi
from tracardi.domain.profile_data import FLAT_PROFILE_FIELD_MAPPING
from tracardi.common.logging.log_handler import get_logger
from tracardi.process_engine.tql.utils.dictonary import flatten
from tracardi.common.dot_notation.dotdict import DotDict
from tracardi.service.events import get_default_mappings_for
from tracardi.domain.tracker_config import TrackerConfig
from tracardi.service.utils.hasher import uuid4_from_md5, hash_id

from tracardi.service.storage.mysql.interface import event_to_profile_dao

logger = get_logger(__name__)


class ConfigurableBridge(NamedEntity):
    config: Optional[dict] = {}

    async def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig) -> Tuple[
        TrackerPayload, TrackerConfig]:
        pass

    @staticmethod
    async def _get_hashed_id(tracker_payload: TrackerPayload) -> Optional[str]:

        for event in tracker_payload.events:
            flat_properties = DotDict({"properties": event.properties})
            event_type = event.type.lower()

            # Check if in custom event to profile mapping for current event type, there is a mapping for merging keys

            custom_event_to_profile_mappings: List[EventToProfile] = await event_to_profile_dao.load_event_to_profile(event_type_id=event_type)

            for custom_mapping_schema in custom_event_to_profile_mappings:
                for event_to_profile_mapping in custom_mapping_schema.event_to_profile:
                    if event_to_profile_mapping.event.value in flat_properties and event_to_profile_mapping.profile.value in FLAT_PROFILE_FIELD_MAPPING:
                        _merge_id = flat_properties[event_to_profile_mapping.event.value]
                        _prefix = FLAT_PROFILE_FIELD_MAPPING[event_to_profile_mapping.profile.value]
                        profile_id = hash_id(_merge_id, _prefix)
                        return profile_id

            # Check if in default event to profile mapping for current event type, there is a mapping for merging keys
            default_event_to_mapping_schema = get_default_mappings_for(event_type, 'copy')

            if default_event_to_mapping_schema is not None:
                for destination, source in default_event_to_mapping_schema.items():  # type: str, str
                    if destination in FLAT_PROFILE_FIELD_MAPPING and source in flat_properties:
                        _merge_id = flat_properties[source]
                        _prefix = FLAT_PROFILE_FIELD_MAPPING[destination]
                        profile_id = hash_id(_merge_id, _prefix)
                        return profile_id

        return None


class WebHookBridge(ConfigurableBridge):

    async def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig) -> Tuple[
        TrackerPayload, TrackerConfig]:

        if self.config is not None:
            if 'generate_profile' in self.config:
                if self.config['generate_profile'] is True:

                    # Check if we can generate primary hashed ids
                    if tracardi.is_apm_on():
                        # Check if there can be a hashed id generated
                        profile_id = await self._get_hashed_id(tracker_payload)
                        if profile_id:
                            tracker_payload.replace_profile(profile_id)

                            sticky_session = self.config.get('sticky_session', True)

                            if sticky_session:
                                session_id = uuid4_from_md5(
                                    md5(f"{tracardi.auto_profile_merging}:{profile_id}".encode()).hexdigest())
                                tracker_payload.replace_session(session_id)

                    # Create random if does not exist

                    if not tracker_payload.session:
                        tracker_payload.replace_session(str(uuid4()))

                    if not tracker_payload.profile:
                        tracker_payload.replace_profile(str(uuid4()))

            if 'replace_profile_id' in self.config:

                replace_profile_id = self.config.get('replace_profile_id', None)

                if replace_profile_id:
                    # There is always o event in webhook
                    flat_properties = flatten(tracker_payload.events[0].properties)
                    if replace_profile_id in flat_properties:
                        profile_id = str(flat_properties.get(replace_profile_id, None))
                        tracker_payload.replace_profile(profile_id)
                        if not tracker_payload.session:
                            # Replace session id with profile ID
                            tracker_payload.replace_session(profile_id)
                        tracker_config.static_profile_id = True

        return tracker_payload, tracker_config


class RestApiBridge(ConfigurableBridge):

    async def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig) -> Tuple[
        TrackerPayload, TrackerConfig]:
        # If REST API is configured to have static Profile ID, set it in tracker config

        if tracker_payload.source.config is not None and tracker_payload.source.config.get('static_profile_id', False):
            tracker_config.static_profile_id = True

        return tracker_payload, tracker_config
