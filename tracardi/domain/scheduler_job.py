from typing import Any
from uuid import uuid4

from tracardi.domain.event import Event
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.domain.entity import Entity


class SchedulerJob(Entity):
    id: str = None
    timestamp: float
    event: Event
    status: str = 'pending'

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid4())

    def to_tracker_payload(self, options=None) -> TrackerPayload:

        if options is None:
            options = {}

        return TrackerPayload(
            metadata=self.event.metadata,
            source=self.event.source,
            session=self.event.session,
            profile=self.event.profile,
            context=self.event.context,
            request=self.event.request,
            events=[EventPayload(type=self.event.type, properties=self.event.properties, options=options)]
        )

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'task',
            SchedulerJob
        )
