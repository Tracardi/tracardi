from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

from tracardi.service.storage.crud import StorageCrud
from .context import Context
from .entity import Entity
from .metadata import Metadata
from .profile import Profile
from .session import Session
from .time import Time


class Event(Entity):
    metadata: Metadata
    type: str
    properties: Optional[dict] = {}

    source: Entity
    session: Session
    profile: Profile = None
    context: Context

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    def replace(self, event):
        self.id = event.id
        self.type = event.type
        self.properties = event.properties
        self.source = event.source
        self.session = event.session
        self.profile = event.profile
        self.context = event.context

    # Persistence

    def storage(self, **kwargs) -> StorageCrud:
        return StorageCrud("event", Event, entity=self)

    @staticmethod
    def new(data: dict) -> 'Event':
        data['id'] = str(uuid4())
        return Event(**data)
