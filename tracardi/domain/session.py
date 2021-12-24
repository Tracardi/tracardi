from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

from .entity import Entity
from .metadata import Metadata
from .time import Time
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo


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
        if isinstance(session, Session):
            self.id = session.id
            self.metadata = session.metadata
            self.operation = session.operation
            self.profile = session.profile
            self.context = session.context
            self.properties = session.properties

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'session',
            Session
        )

    @staticmethod
    def new() -> 'Session':
        return Session(id=str(uuid4()))
