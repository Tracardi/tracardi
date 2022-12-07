from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel

from .entity import Entity
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo


class SessionTime(BaseModel):
    insert: Optional[datetime]
    update: Optional[datetime] = None
    timestamp: Optional[int] = 0
    duration: float = 0

    def __init__(self, **data: Any):

        now = datetime.utcnow()

        if 'insert' not in data:
            data['insert'] = now

        if 'timestamp' not in data:
            data['timestamp'] = datetime.timestamp(now)

        if 'duration' not in data:
            data['duration'] = 0

        super().__init__(**data)


class SessionMetadata(BaseModel):
    time: SessionTime = SessionTime()
    channel: Optional[str] = None


class SessionContext(dict):

    def get_time_zone(self) -> str:
        try:
            return self['time']['tz']
        except KeyError:
            return 'utc'

    def get_platform(self):
        try:
            return self['browser']['local']['device']['platform']
        except KeyError:
            return None

    def get_browser_name(self):
        try:
            return self['browser']['local']['browser']['name']
        except KeyError:
            return None


class Session(Entity):
    metadata: SessionMetadata
    operation: Operation = Operation()
    profile: Optional[Entity] = None
    context: Optional[SessionContext] = {}
    properties: Optional[dict] = {}

    def __init__(self, **data: Any):

        if 'context' in data and not isinstance(data['context'], SessionContext):
            data['context'] = SessionContext(data['context'])

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
            Session,
            exclude={"operation": ...},
            multi=True
        )
