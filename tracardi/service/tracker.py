from typing import Optional

from com_tracardi.service.profiler_calculator import calculate_statistics
from tracardi.context import get_context
from tracardi.domain.bridges.configurable_bridges import WebHookBridge, RestApiBridge, ConfigurableBridge
from tracardi.exceptions.exception import BlockedException
from tracardi.service.license import License
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.service.tracking.source_validation import validate_source
from tracardi.service.tracker_config import TrackerConfig
from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import get_logger

if License.has_license():
    from com_tracardi.workers.collector import run_com_tracker_worker, run_com_tracker
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

            context.profiler.measure('tracker-validation')

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

            context.profiler.measure('tracker-bridge')

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
            if len(_measures) > 100:

                # Calculate and print statistics
                result = calculate_statistics(_measures)

                print("\nTime Statistics:")
                print(result)

                context.profiler.reset_measures()
                _measures = []

            else:
                _measures.append(context.profiler.get_measures())
