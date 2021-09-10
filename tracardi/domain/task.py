import asyncio
from typing import Any, Optional, Coroutine
from uuid import uuid4

from app.api.track.service.tracker import track_event
from app.utils.network import local_ip
from tracardi.domain.payload.event_payload import EventPayload

from tracardi.domain.payload.tracker_payload import TrackerPayload

from tracardi.domain.context import Context
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
    context: Context
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

    def run(self):
        tracker_payload = self.event.to_tracker_payload()

        async def _task():
            try:
                return await track_event(tracker_payload, ip=local_ip), self
            except Exception as e:
                print(str(e))
                self.status = 'error'
                return None, self

        return asyncio.create_task(_task())
