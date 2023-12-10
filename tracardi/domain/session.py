import uuid

from datetime import datetime
from typing import Optional, Any

from pydantic import ConfigDict, BaseModel, PrivateAttr

from .entity import Entity
from .marketing import UTM
from .metadata import OS, Device, Application

from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo


class SessionTime(BaseModel):
    insert: Optional[datetime] = None
    update: Optional[datetime] = None
    timestamp: Optional[float] = 0
    duration: float = 0
    weekday: Optional[int] = None

    def __init__(self, **data: Any):

        now = datetime.utcnow()

        if 'insert' not in data:
            data['insert'] = now

        if 'timestamp' not in data:
            data['timestamp'] = datetime.timestamp(now)

        if 'duration' not in data:
            data['duration'] = 0

        super().__init__(**data)

        self.weekday = self.insert.weekday()


class SessionMetadata(BaseModel):
    time: SessionTime = SessionTime(insert=datetime.utcnow(), timestamp=datetime.timestamp(datetime.utcnow()))
    channel: Optional[str] = None
    aux: Optional[dict] = {}
    status: Optional[str] = None


class SessionContext(dict):

    def get_time_zone(self) -> Optional[str]:
        try:
            return self['time']['tz']
        except KeyError:
            return None

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

    device: Optional[Device] = Device()
    os: Optional[OS] = OS()
    app: Optional[Application] = Application()

    utm: Optional[UTM] = UTM()

    context: Optional[SessionContext] = {}
    properties: Optional[dict] = {}
    traits: Optional[dict] = {}
    aux: Optional[dict] = {}

    _updated_in_workflow: bool = PrivateAttr(False)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: Any):

        if 'context' in data and not isinstance(data['context'], SessionContext):
            data['context'] = SessionContext(data['context'])

        super().__init__(**data)

    def set_updated_in_workflow(self, state=True):
        self._updated_in_workflow = state

    def is_updated_in_workflow(self) -> bool:
        return self._updated_in_workflow

    def fill_meta_data(self):
        """
        Used to fill metadata with default current index and id.
        """
        self._fill_meta_data('session')

    def replace(self, session):
        if isinstance(session, Session):
            self.id = session.id
            self.metadata = session.metadata
            self.operation = session.operation
            self.profile = session.profile
            self.context = session.context
            self.properties = session.properties
            self.traits = self.traits
            self.aux = session.aux
            self.device = session.device
            self.os = session.os
            self.app = session.app

    def is_reopened(self) -> bool:
        return self.operation.new or self.metadata.status == 'ended'

    def has_not_saved_changes(self) -> bool:
        return self.operation.new or self.operation.needs_update()

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'session',
            Session,
            exclude={"operation": ...},
            multi=True
        )

    @staticmethod
    def new(id: Optional[str] = None) -> 'Session':
        session = Session(
            id=str(uuid.uuid4()) if not id else id,
            metadata=SessionMetadata()
        )
        session.fill_meta_data()
        session.operation.new = True

        return session
