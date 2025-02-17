from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel
# from pydantic import ConfigDict, BaseModel, PrivateAttr
# from user_agents import parse

# from .entity import Entity
# from .marketing import UTM
# from .metadata import OS, Device, Application
from .time import Time

# from .value_object.operation import Operation
# from .value_object.storage_info import StorageInfo
from tracardi.common.time.date import now_in_utc


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


# class Session(Entity):
#     metadata: SessionMetadata
#     operation: Operation = Operation()
#     profile: Optional[Entity] = None
#
#     device: Optional[Device] = Device()
#     os: Optional[OS] = OS()
#     app: Optional[Application] = Application()
#
#     utm: Optional[UTM] = UTM()
#
#     context: Optional[dict] = {}
#     properties: Optional[dict] = {}
#     traits: Optional[dict] = {}
#     aux: Optional[dict] = {}
#
#     _updated_in_workflow: bool = PrivateAttr(False)
#
#     model_config = ConfigDict(frozen=False)
#
#     def __init__(self, **data: Any):
#         super().__init__(**data)
#         self._is_frozen = False  # Internal flag to manage mutability

    # def freeze(self):
    #     self._is_frozen = True
    #
    # def unfreeze(self):
    #     self._is_frozen = False

    # def __setattr__(self, key, value):
    #     if getattr(self, "_is_frozen", False) and key != '_is_frozen':
    #         raise TypeError(f"Cannot modify frozen instance: attribute '{key}' is read-only")
    #     super().__setattr__(key, value)
    #
    # def is_new(self) -> bool:
    #     return self.operation.new

    # def set_new(self, flag=True):
    #     self.operation.new = flag
    #
    # def set_updated(self, flag=True):
    #     self.operation.update = flag
    #
    # def is_updated(self) -> bool:
    #     return self.operation.update
    #
    # def set_updated_in_workflow(self, state=True):
    #     self._updated_in_workflow = state
    #
    # def is_updated_in_workflow(self) -> bool:
    #     return self._updated_in_workflow

    # def fill_meta_data(self):
    #     """
    #     Used to fill metadata with default current index and id.
    #     """
    #     self._fill_meta_data('session')

    # def replace(self, session):
    #     if isinstance(session, Session):
    #         self.unfreeze()
    #         self.id = session.id
    #         self.metadata = session.metadata
    #         self.operation = session.operation
    #         self.profile = session.profile
    #         self.context = session.context
    #         self.properties = session.properties
    #         self.traits = self.traits
    #         self.aux = session.aux
    #         self.device = session.device
    #         self.os = session.os
    #         self.app = session.app
    #         self.freeze()

    # def is_reopened(self) -> bool:
    #     return self.operation.new or self.metadata.status == 'ended'

    # def has_not_saved_changes(self) -> bool:
    #     return self.operation.new or self.operation.needs_update()

    # def has_data_to_geo_locate(self) -> bool:
    #     return self.device.ip and self.device.ip != '0.0.0.0' and self.device.geo.is_empty()

    # def get_ip(self) -> Optional[str]:
    #     try:
    #         if ',' not in self.device.ip:
    #             return self.device.ip
    #
    #         ips = self.device.ip.split(',')
    #         return ips[0]
    #     except Exception:
    #         return None

    # def get_time_zone(self) -> Optional[str]:
    #     try:
    #         return self.context['time']['tz']
    #     except KeyError:
    #         return None

    # def get_platform(self):
    #     try:
    #         return self.context['browser']['local']['device']['platform']
    #     except KeyError:
    #         return None
    #
    # def get_browser_name(self):
    #     try:
    #         return self.context['browser']['local']['browser']['name']
    #     except KeyError:
    #         return None
    #
    # def get_user_agent(self) -> Optional[str]:
    #     try:
    #         _user_agent_string = self.context['browser']['local']['browser']['userAgent']
    #         if not _user_agent_string:
    #             return None
    #         return parse(_user_agent_string)
    #     except Exception:
    #         return None

    # @staticmethod
    # def storage_info() -> StorageInfo:
    #     return StorageInfo(
    #         'session',
    #         Session,
    #         exclude={"operation": ...},
    #         multi=True
    #     )

    # @staticmethod
    # def new(id: Optional[str] = None, profile_id: str = None) -> 'Session':
    #     session = Session(
    #         id=str(uuid.uuid4()) if not id else id,
    #         metadata=SessionMetadata.new()
    #     )
    #     # session.fill_meta_data()
    #     session.set_new()
    #     if profile_id is not None:
    #         session.profile = Entity(id=profile_id)
    #
    #     return session

