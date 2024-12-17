import uuid

from datetime import datetime
from typing import Optional, Any

from pydantic import ConfigDict, BaseModel, PrivateAttr

from .entity import Entity, PrimaryEntity
from .marketing import UTM
from .metadata import OS, Device, Application
from .time import Time

from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo
from ..service.utils.date import now_in_utc


class SessionTime(Time):
    timestamp: Optional[float] = 0
    duration: float = 0
    weekday: Optional[int] = None

    def __init__(self, **data: Any):

        if 'duration' not in data:
            data['duration'] = 0

        super().__init__(**data)

        self.weekday = self.insert.weekday()

        if self.timestamp == 0:
            self.timestamp = datetime.timestamp(now_in_utc())

    @staticmethod
    def new() -> 'SessionTime':
        return SessionTime()

class SessionMetadata(BaseModel):
    time: SessionTime = SessionTime()
    channel: Optional[str] = None
    aux: Optional[dict] = {}
    status: Optional[str] = None

    @staticmethod
    def new() -> 'SessionMetadata':
        return SessionMetadata(time=SessionTime.new())


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


    def is_new(self) -> bool:
        return self.operation.new

    def set_new(self, flag=True):
        self.operation.new = flag

    def set_updated(self, flag=True):
        self.operation.update = flag


    def is_updated(self) -> bool:
        return self.operation.update

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

    def has_data_to_geo_locate(self) -> bool:
        return self.device.ip and self.device.ip != '0.0.0.0' and self.device.geo.is_empty()

    def get_ip(self) -> Optional[str]:
        try:
            if ',' not in self.device.ip:
                return self.device.ip

            ips = self.device.ip.split(',')
            return ips[0]
        except Exception:
            return None

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'session',
            Session,
            exclude={"operation": ...},
            multi=True
        )

    @staticmethod
    def new(id: Optional[str] = None, profile_id: str=None) -> 'Session':
        session = Session(
            id=str(uuid.uuid4()) if not id else id,
            metadata=SessionMetadata.new()
        )
        session.fill_meta_data()
        session.set_new()
        if profile_id is not None:
            session.profile = Entity(id=profile_id)

        return session


class FrozenSession(Session):
    class Config:
        frozen = True