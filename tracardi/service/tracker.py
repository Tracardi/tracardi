from typing import Optional

from tracardi.context import get_context
from tracardi.domain.bridges.configurable_bridges import WebHookBridge, RestApiBridge, ConfigurableBridge
from tracardi.common.exception.exception import InvalidBotTrafficException
from tracardi.service.license import License
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.tracking.source_validation import validate_source
from tracardi.domain.tracker_config import TrackerConfig
from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.common.logging.log_handler import get_logger

if License.has_license():
    from com_tracardi.workers.collector import run_com_tracker_worker, run_com_tracker
    from com_tracardi.service.profiler_calculator import calculate_statistics
else:
    from tracardi.service.tracking.tracker import os_tracker

logger = get_logger(__name__)
_measures = []


class Tracker:

    def __init__(self, tracker_config: TrackerConfig):
        self.tracker_config = tracker_config

    @staticmethod
    def get_bridge(tracker_payload: TrackerPayload) -> Optional[ConfigurableBridge]:
        if not isinstance(tracker_payload.source, EventSource):
            logger.error("Can't configure bridge. Method get_bridge used before "
                         "EventSource was created.")

        # TODO permanent_profile_id is kept in tracker_payload.source.permanent_profile_id
        # TODO GUI should change it in tracker_payload.source. That is why we copy it

        if isinstance(tracker_payload.source, EventSource) and isinstance(tracker_payload.source.config, dict):
            tracker_payload.source.config['static_profile_id'] = tracker_payload.source.permanent_profile_id

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

        context = get_context()
        try:

            context.profiler.measure('tracker-starts')

            if tracardi.disallow_bot_traffic and tracker_payload.is_bot():
                raise InvalidBotTrafficException(f"Traffic from bot is not allowed.")

                # Trim ids - spaces are frequent issues

            if tracker_payload.source:
                tracker_payload.source.id = str(tracker_payload.source.id).strip()
            if tracker_payload.session:
                tracker_payload.session.id = str(tracker_payload.session.id).strip()
                if tracker_payload.session.id == "":
                    tracker_payload.session = None
            if tracker_payload.profile:
                tracker_payload.profile.id = str(tracker_payload.profile.id).strip()
                if tracker_payload.profile.id == "":
                    tracker_payload.profile = None

            # Validate event source

            source = await validate_source(self.tracker_config, tracker_payload)

            logger.debug(f"Source {source.id} validated.")

            context.profiler.measure('tracker-validation')

            # Update tracker source with full event source object
            tracker_payload.source = source

            # If there is a configurable bridge get it and set up tracker_payload and tracker_config
            print(9, tracker_payload.events[0].properties)
            configurable_bridge = self.get_bridge(tracker_payload)

            if configurable_bridge:
                tracker_payload, self.tracker_config = await configurable_bridge.configure(
                    tracker_payload,
                    self.tracker_config
                )
            print(10, tracker_payload.events[0].properties)
            # Is source ephemeral
            if tracker_payload.source.transitional is True:
                tracker_payload.set_ephemeral()

            context.profiler.measure('tracker')

            if not License.has_license():
                return await os_tracker(
                    source,
                    tracker_payload,
                    self.tracker_config,
                    tracking_start
                )

            # Only commercial

            # Split async and sync events
            should_run_on_queue = tracker_payload.queue_required() and not tracker_payload.has_sync_events()

            if not should_run_on_queue:
                # Process without queue
                return await run_com_tracker(source, tracker_payload, self.tracker_config)

            # Queue
            await run_com_tracker_worker(
                self.tracker_config,
                tracker_payload,
                source)

            return {}
        finally:
            global _measures
            context.profiler.measure('tracker-ends')
            if len(_measures) > 5000:

                if License.has_license():
                    # Calculate and print statistics
                    result = calculate_statistics(_measures)

                    print("\nTime Statistics:")
                    print(result)

                context.profiler.reset_measures()
                _measures = []

            else:
                _measures.append(context.profiler.get_measures())
