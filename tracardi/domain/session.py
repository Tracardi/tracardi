from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

from .entity import Entity
from .metadata import Metadata
from .time import Time
from tracardi.service.storage.crud import StorageCrud
from .value_object.operation import Operation


class Session(Entity):
    metadata: Optional[Metadata]
    operation: Operation = Operation()
    profile: Optional[Entity] = None
    context: Optional[dict] = {}
    properties: Optional[dict] = {}

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    def replace(self, session):
        self.metadata = session.metadata
        self.profile = session.profile
        self.context = session.context
        self.id = session.id
        self.properties = session.properties
        self.operation = session.operation

    def storage(self, **kwargs) -> StorageCrud:
        return StorageCrud("session", Session, entity=self)

    @staticmethod
    def new() -> 'Session':
        return Session(id=str(uuid4()))
