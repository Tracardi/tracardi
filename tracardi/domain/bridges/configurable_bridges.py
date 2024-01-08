import logging
from typing import Optional, Tuple
from uuid import uuid4

from tracardi.config import tracardi
from tracardi.domain.console import Console
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile_data import PREFIX_EMAIL_MAIN, PREFIX_PHONE_MAIN
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.console_log import ConsoleLog
from tracardi.exceptions.exception_service import get_traceback
from tracardi.service.tracker_config import TrackerConfig
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.utils.hasher import hash_id

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ConfigurableBridge(NamedEntity):
    config: Optional[dict] = {}

    def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig, console_log: ConsoleLog) -> Tuple[
        TrackerPayload, TrackerConfig, ConsoleLog]:
        pass


class WebHookBridge(ConfigurableBridge):

    def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig, console_log: ConsoleLog) -> Tuple[
        TrackerPayload, TrackerConfig, ConsoleLog]:

        if self.config is not None:
            if 'generate_profile' in self.config:
                if self.config['generate_profile'] is True:

                    if 'replace_session_id' in self.config:
                        try:
                            session_id_ref = self.config['replace_session_id'].strip()
                            if bool(session_id_ref):
                                # Webhooks have only one event, so it is save to get it from tracker_payload.events[0]
                                session_id = tracker_payload.events[0].properties[session_id_ref]
                                tracker_payload.replace_session(session_id)
                        except KeyError as e:
                            message = f"Could not generate set session for a webhook. " \
                                      f"Event stays session-less. " \
                                      f"Probable reason: Missing event properties: {str(e)}"
                            logger.error(message)
                            console_log.append(Console(
                                flow_id=None,
                                node_id=None,
                                event_id=None,
                                profile_id=get_entity_id(tracker_payload.profile),
                                origin='tracker',
                                class_name=__name__,
                                module=__name__,
                                type='error',
                                message=message,
                                traceback=get_traceback(e)
                            ))

                    if 'replace_profile_id' in self.config:
                        try:
                            profile_id_ref = self.config['replace_profile_id'].strip()

                            # If exists
                            if bool(profile_id_ref):

                                # Webhooks have only one event, so it is save to get it from self.events[0]
                                _properties = tracker_payload.events[0].properties
                                _profile_id_value = _properties[profile_id_ref]

                                if 'identify_profile_by' not in self.config:
                                    # Old way to handle identification
                                    profile_id = _properties[profile_id_ref]
                                else:
                                    # New way to handle identification
                                    if self.config['identify_profile_by'] == 'e-mail':
                                        profile_id = hash_id(_profile_id_value, PREFIX_EMAIL_MAIN)

                                    elif self.config['identify_profile_by'] == 'phone':
                                        profile_id = hash_id(_profile_id_value, PREFIX_PHONE_MAIN)

                                    elif self.config['identify_profile_by'] == 'id':
                                        profile_id = _profile_id_value

                                    else:
                                        profile_id = None

                                if profile_id is not None:
                                    tracker_payload.replace_profile(profile_id)

                        except KeyError as e:
                            message = f"Could not generate profile and session for a webhook. " \
                                      f"Event stays profile-less. " \
                                      f"Probable reason: Missing event properties: {str(e)}"
                            logger.error(message)
                            console_log.append(Console(
                                flow_id=None,
                                node_id=None,
                                event_id=None,
                                profile_id=get_entity_id(tracker_payload.profile),
                                origin='tracker',
                                class_name=__name__,
                                module=__name__,
                                type='error',
                                message=message,
                                traceback=get_traceback(e)
                            ))

                    if not tracker_payload.profile:
                        tracker_payload.replace_profile(str(uuid4()))

                    if not tracker_payload.session:
                        tracker_payload.replace_session(str(uuid4()))

        return tracker_payload, tracker_config, console_log


class RestApiBridge(ConfigurableBridge):

    def configure(self, tracker_payload: TrackerPayload, tracker_config: TrackerConfig, console_log: ConsoleLog) -> Tuple[
        TrackerPayload, TrackerConfig, ConsoleLog]:

        # If REST API is configured to have static Profile ID, set it in tracker config

        if tracker_payload.source.config is not None and tracker_payload.source.config.get('static_profile_id', False):
            tracker_config.static_profile_id = True

        return tracker_payload, tracker_config, console_log
