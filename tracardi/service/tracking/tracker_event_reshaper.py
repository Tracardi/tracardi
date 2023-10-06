import traceback

from typing import Tuple, Optional

from tracardi.service.tracking.tracker_event_props_reshaper import EventDataReshaper
from tracardi.domain.payload.event_payload import ProcessStatus, EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.exception_service import get_traceback
from tracardi.service.cache_manager import CacheManager
from tracardi.service.notation.dot_accessor import DotAccessor

cache = CacheManager()


class EventsReshaper:

    def __init__(self, tracker_payload: TrackerPayload):
        self.tracker_payload = tracker_payload

    @staticmethod
    async def _reshape_event(event: EventPayload, session_context: dict) -> Optional[
        Tuple[dict, dict, Optional[dict]]]:

        reshape_schemas = await cache.event_reshaping(event.type, ttl=15)

        if reshape_schemas is not None:
            resharper = EventDataReshaper(
                # Only this data can be used in the reshaping
                dot=DotAccessor(
                    event={
                        "type": event.type,
                        "properties": event.properties,
                        "context": event.context
                    },
                    session={"context": session_context})
            )
            return resharper.reshape(schemas=reshape_schemas)

        return None

    async def reshape_events(self) -> TrackerPayload:
        """
        Returns reshaped events, if there is not reshape for event the original event is returned.
        The same with session.
        """

        for event in self.tracker_payload.events:

            # Skip invalid
            if event.validation and event.validation.error:
                continue

            try:
                result = await self._reshape_event(
                    event,
                    self.tracker_payload.context)

                if result is not None:
                    event_properties, event_context, session_context = result

                    if event_properties is not None:
                        event.properties = event_properties

                    if event_context is not None:
                        event.context = event_context

                    event.reshaping = ProcessStatus(error=False)

                    if session_context is not None:
                        self.tracker_payload.context = session_context

            except Exception as e:
                event.reshaping = ProcessStatus(
                    error=True,
                    message=str(e),
                    trace=get_traceback(e)
                )

        return self.tracker_payload
