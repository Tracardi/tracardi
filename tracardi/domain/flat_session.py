from datetime import datetime

import uuid

from typing import Optional, Dict
from system.adapter.os.bigdata.elastic.model.storage_record import StorageRecord

from tracardi.common.time.date import now_in_utc
from tracardi.domain.entity import FlatEntity
from tracardi.domain.time import Time
from user_agents import parse


class FlatSession(FlatEntity):

    PRIMARY_ID = "primary.id"
    METADATA = "metadata"
    METADATA_STATUS = "metadata.status"
    METADATA_TIME_TIMESTAMP = "metadata.time.timestamp"
    METADATA_TIME_DURATION = "metadata.time.duration"
    METADATA_TIME_WEEKDAY = "metadata.time.weekday"
    METADATA_TIME_TZ = "metadata.time.tz"
    METADATA_TIME_OFFSET = "metadata.time.offset"
    METADATA_CHANNEL = "metadata.channel"
    METADATA_HIT_REFERER = "metadata.hit.referer"
    METADATA_DEVICE_NAME = "metadata.device.name"
    METADATA_DEVICE_BRAND = "metadata.device.brand"
    METADATA_DEVICE_MODEL = "metadata.device.model"
    METADATA_DEVICE_TYPE = "metadata.device.type"
    METADATA_DEVICE_TOUCH = "metadata.device.touch"
    METADATA_DEVICE_IP = "metadata.device.ip"
    METADATA_DEVICE_RESOLUTION_WIDTH = "metadata.device.resolution.width"
    METADATA_DEVICE_RESOLUTION_HEIGHT = "metadata.device.resolution.height"
    METADATA_DEVICE_RESOLUTION_ORIENTATION = "metadata.device.resolution.orientation"
    METADATA_DEVICE_GPU_VENDOR_ID = "metadata.device.gpu.vendor.id"
    METADATA_DEVICE_GPU_VENDOR_NAME = "metadata.device.gpu.vendor.name"
    METADATA_DEVICE_GPU_RENDERER_NAME = "metadata.device.gpu.renderer.renderer"
    METADATA_DEVICE_COLOR_DEPTH = "metadata.device.color_depth"
    METADATA_DEVICE_ORIENTATION = "metadata.device.orientation"
    METADATA_DEVICE_GEO_COUNTRY_NAME = "metadata.device.geo.country.name"
    METADATA_DEVICE_GEO_COUNTRY_CODE = "metadata.device.geo.country.code"
    METADATA_DEVICE_GEO_COUNTY = "metadata.device.geo.county"
    METADATA_DEVICE_GEO_CITY = "metadata.device.geo.city"
    METADATA_DEVICE_GEO_POSTAL = "metadata.device.geo.postal"
    METADATA_DEVICE_GEO_LATITUDE = "metadata.device.geo.latitude"
    METADATA_DEVICE_GEO_LONGITUDE = "metadata.device.geo.longitude"
    METADATA_DEVICE_GEO_LOCATION = "metadata.device.geo.location"
    METADATA_OS_NAME = "metadata.os.name"
    METADATA_OS_VERSION = "metadata.os.version"
    METADATA_APP_TYPE = "metadata.app.type"
    METADATA_APP_NAME = "metadata.app.name"
    METADATA_APP_VERSION = "metadata.app.version"
    METADATA_APP_LANGUAGE = "metadata.app.language"
    METADATA_APP_BOT = "metadata.app.bot"
    METADATA_APP_RESOLUTION = "metadata.app.resolution"
    METADATA_UTM_SOURCE = "metadata.utm.source"
    METADATA_UTM_MEDIUM = "metadata.utm.medium"
    METADATA_UTM_CAMPAIGN = "metadata.utm.campaign"
    METADATA_UTM_TERM = "metadata.utm.term"
    METADATA_UTM_CONTENT = "metadata.utm.content"
    PROFILE_ID = "profile.id"
    PROFILE_PRIMARY_ID = "profile.primary.id"
    CONTEXT = "context"
    PROPERTIES = "properties"
    TRAITS = "traits"
    AUX = "aux"

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

        default[FlatSession.ID] = str(uuid.uuid4()) if not id else id
        default[FlatSession.METADATA] = {
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
            _user_agent_string = self.get_or_none('context.browser.local.browser.userAgent')
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
                'profile',
                'context',
                'properties',
                'operation',
            }
            self.freeze()


    def set_updated_in_workflow(self, state=True):
        self._updated_in_workflow = state


    def is_updated_in_workflow(self) -> bool:
        return self._updated_in_workflow


    # -------------------
    #  PROPERTIES
    # -------------------

    @property
    def primary_id(self):
        return self.get(FlatSession.PRIMARY_ID)

    @primary_id.setter
    def primary_id(self, value):
        self.set(FlatSession.PRIMARY_ID, value)
