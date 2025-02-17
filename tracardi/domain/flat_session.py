from datetime import datetime

import uuid

from typing import Optional, Dict

from tracardi.common.time.date import now_in_utc
from tracardi.domain.entity import FlatEntity
from tracardi.domain.time import Time
from system.adapter.os.bigdata.elastic.model.storage_record import StorageRecord
from user_agents import parse


class FlatSession(FlatEntity):

    def __init__(self, dictionary):
        super().__init__(dictionary)
        self._is_frozen = False  # Internal flag to manage mutability
        self._updated_in_workflow = False

    def freeze(self):
        self._is_frozen = True

    def unfreeze(self):
        self._is_frozen = False

    @staticmethod
    def new(id: Optional[str] = None, profile_id: str = None, default: Optional[Dict] = None) -> 'FlatSession':
        time = Time()
        time_dict = time.model_dump(mode='json')
        time_dict["timestamp"] = datetime.timestamp(now_in_utc())
        time_dict["duration"] = 0
        time_dict["weekday"] = time.insert.weekday()

        if not default:
            default = {}

        default['id'] = str(uuid.uuid4()) if not id else id
        default['metadata'] = {
            "time": time_dict,
            "channel": None,
            "aux": {},
            "status": None
        }

        flat_session = FlatSession(default)

        flat_session.set_new()
        if profile_id is not None:
            flat_session['profile'] = dict(id=profile_id)

        return flat_session

    def is_new(self) -> bool:
        return bool(self.get('operation.new', False))

    def is_updated(self) -> bool:
        return self.get('operation.update', False)

    def set_new(self, flag=True):
        self.set('operation.new', flag)

    def set_updated(self, flag=True):
        self.set('operation.update', flag)

    @staticmethod
    def from_es_storage_record(record: StorageRecord) -> Optional['FlatSession']:
        if record is None:
            return None

        fs = FlatSession(dict(record))
        fs.set_new(False)
        fs.set_updated(False)
        fs.set_meta_data(record.get_meta_data())
        return fs

    def get_user_agent(self) -> Optional[str]:
        try:
            _user_agent_string = self.get('context.browser.local.browser.userAgent', None)
            if not _user_agent_string:
                return None
            return parse(_user_agent_string)
        except Exception:
            return None

    def is_reopened(self) -> bool:
        return self['operation.new'] or self['metadata.status'] == 'ended'

    def get_time_zone(self) -> Optional[str]:
        return self.get('context.time.tz', None)

    def has_not_saved_changes(self) -> bool:
        return self.get('operation.new', False) or self.get('operation.update', False)

    def has_data_to_geo_locate(self) -> bool:
        return self.get('device.ip', None) != '0.0.0.0' and self.get('device.geo.country.name', None)

    def get_ip(self) -> Optional[str]:
        try:
            if ',' not in self['device.ip']:
                return self['device.ip']

            ips = self['device.ip'].split(',')
            return ips[0]
        except Exception:
            return None

    def replace(self, session: 'FlatSession'):
        if isinstance(session, FlatSession):
            self.unfreeze()
            self.map(session) << {
                'id',
                'metadata',
                'operation',
                'profile',
                'context',
                'properties',
                'aux',
                'device',
                'os',
                'app',
            }
            self.freeze()


    def set_updated_in_workflow(self, state=True):
        self._updated_in_workflow = state


    def is_updated_in_workflow(self) -> bool:
        return self._updated_in_workflow
