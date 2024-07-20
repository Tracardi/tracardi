from typing import Optional

from tracardi.domain.bridges.configurable_bridges import WebHookBridge, RestApiBridge, ConfigurableBridge
from tracardi.exceptions.exception import BlockedException
from tracardi.service.change_monitoring.field_change_logger import FieldChangeLogger
from tracardi.service.license import License
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.tracking.source_validation import validate_source
from tracardi.service.tracker_config import TrackerConfig
from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import get_logger

if License.has_license():
    from com_tracardi.service.tracking.tracker import com_tracker
else:
    from tracardi.service.tracking.tracker import os_tracker

logger = get_logger(__name__)


class Tracker:

    def __init__(self, tracker_config: TrackerConfig):
        self.tracker_config = tracker_config

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

        if tracardi.disallow_bot_traffic and tracker_payload.is_bot():
            raise BlockedException(f"Traffic from bot is not allowed.")

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

        field_change_logger = FieldChangeLogger()

        if License.has_license():
            result = await com_tracker(
                field_change_logger,
                source,
                tracker_payload,
                self.tracker_config,
                tracking_start
            )
        else:
            result = await os_tracker(
                field_change_logger,
                source,
                tracker_payload,
                self.tracker_config,
                tracking_start
            )

        # if result and tracardi.enable_errors_on_response:
        #     result['errors'] += self.console_log.get_errors()
        #     result['warnings'] += self.console_log.get_warnings()

        return result
