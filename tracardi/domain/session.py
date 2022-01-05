from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel

from .entity import Entity
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo


class SessionTime(BaseModel):
    insert: Optional[datetime]
    timestamp: Optional[int] = 0

    def __init__(self, **data: Any):
        if 'insert' not in data:
            data['insert'] = datetime.utcnow()

        data['timestamp'] = datetime.timestamp(datetime.utcnow())

        super().__init__(**data)


class SessionMetadata(BaseModel):
    time: SessionTime = SessionTime()


class Session(Entity):
    metadata: SessionMetadata
    operation: Operation = Operation()
    profile: Optional[Entity] = None
    context: Optional[dict] = {}
    properties: Optional[dict] = {}

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

    def get_platform(self):
        try:
            return self.context['browser']['local']['device']['platform']
        except KeyError:
            return None

    def get_browser_name(self):
        try:
            return self.context['browser']['local']['browser']['name']
        except KeyError:
            return None
