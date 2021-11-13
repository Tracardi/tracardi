from typing import Any, Optional
from uuid import uuid4
from tracardi.domain.payload.event_payload import EventPayload

from tracardi.domain.payload.tracker_payload import TrackerPayload

from tracardi.domain.metadata import Metadata
from tracardi.domain.value_object.storage_info import StorageInfo

from tracardi.domain.entity import Entity


class TaskEvent(Entity):
    metadata: Metadata
    type: str
    properties: Optional[dict] = {}

    source: Entity
    session: Entity
    profile: Entity
    context: Optional[dict] = {}
    options: Optional[dict] = {}

    def to_tracker_payload(self) -> TrackerPayload:
        return TrackerPayload(
            metadata=self.metadata,
            source=self.source,
            session=self.session,
            profile=self.profile,
            context=self.context,
            events=[EventPayload(type=self.type, properties=self.properties, options=self.options)]
        )


class Task(Entity):
    id: str = None
    timestamp: float
    event: TaskEvent
    status: str = 'pending'

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid4())

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'task',
            Task
        )
