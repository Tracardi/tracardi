from datetime import datetime
from typing import Optional
from uuid import uuid4
from .entity import Entity
from .event_metadata import EventMetadata
from pydantic import BaseModel, root_validator
from typing import Tuple

from .value_object.storage_info import StorageInfo

COLLECTED = 'collected'
PROCESSED = 'processed'


class Tags(BaseModel):
    values: Tuple['str', ...] = ()
    count: int = 0

    class Config:
        validate_assignment = True

    @root_validator
    def total_tags(cls, values):
        values["count"] = len(values.get("values"))
        return values


class EventSession(Entity):
    start: datetime = datetime.utcnow()
    duration: float = 0


class Event(Entity):
    metadata: EventMetadata
    type: str
    properties: Optional[dict] = {}
    update: bool = False

    source: Entity
    session: Optional[EventSession] = None
    profile: Optional[Entity] = None
    context: Optional[dict] = {}
    request: Optional[dict] = {}
    config: Optional[dict] = {}
    tags: Tags = Tags()
    aux: dict = {}

    def replace(self, event):
        if isinstance(event, Event):
            self.id = event.id
            self.metadata = event.metadata
            self.type = event.type
            self.properties = event.properties
            # do not replace those - read only
            # self.source = event.source
            # self.session = event.session
            # self.profile = event.profile
            self.context = event.context
            self.config = event.config
            self.tags = event.tags
            self.aux = event.aux

    def is_persistent(self) -> bool:
        if 'save' in self.config and isinstance(self.config['save'], bool):
            return self.config['save']
        else:
            return True

    @staticmethod
    def new(data: dict) -> 'Event':
        data['id'] = str(uuid4())
        return Event(**data)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'event',
            Event,
            multi=True
        )
