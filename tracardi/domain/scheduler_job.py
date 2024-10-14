from typing import Any, Optional
from uuid import uuid4

from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.entity import Entity


class SchedulerJob(Entity):
    id: Optional[str] = None
    timestamp: float
    flat_event: FlatEvent
    status: str = 'pending'

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid4())

    def to_tracker_payload(self, options=None) -> TrackerPayload:

        if options is None:
            options = {}

        return TrackerPayload(
            metadata=self.flat_event['metadata'],
            source=self.flat_event['source'],
            session=self.flat_event['session'],
            profile=self.flat_event['profile'],
            context=self.flat_event['context'],
            request=self.flat_event['request'],
            events=[EventPayload(type=self.flat_event.type, properties=self.flat_event.properties, options=options)]
        )
