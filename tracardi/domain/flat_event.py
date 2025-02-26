from collections import defaultdict

from typing import Optional, List, Dict, Generator, Tuple
from uuid import uuid4

from .entity import Entity, FlatEntity
from ..common.time.date import now_in_utc


class FlatEvent(FlatEntity):
    PROFILE_ID = 'profile.id'
    SESSION_ID = 'session.id'
    UTM_SOURCE = 'utm.source'
    UTM_MEDIUM = 'utm.medium'
    UTM_CAMPAIGN = 'utm.campaign'
    UTM_TERM = 'utm.term'
    UTM_CONTENT = 'utm.content'
    HIT_ID = 'hit.id'
    HIT_CATEGORY = 'hit.category'
    HIT_QUERY = 'hit.query'
    HIT_REFERER = 'hit.referer'
    HIT_URL = 'hit.url'
    HIT_NAME = 'hit.name'
    APP_RESOLUTION = 'app.resolution'
    APP_LANGUAGE = 'app.language'
    APP_VERSION = 'app.version'
    APP_NAME = 'app.name'
    APP_BOT = 'app.bot'
    APP_TYPE = 'app.type'
    OS_VERSION = 'os.version'
    OS_NAME = 'os.name'
    DEVICE_GEO_POSTAL = 'device.geo.postal'
    DEVICE_GEO_LOCATION = 'device.geo.location'
    DEVICE_GEO_LONGITUDE = 'device.geo.longitude'
    DEVICE_GEO_LATITUDE = 'device.geo.latitude'
    DEVICE_GEO_CITY = 'device.geo.city'
    DEVICE_GEO_COUNTY = 'device.geo.county'
    DEVICE_GEO_COUNTRY_CODE = 'device.geo.country.code'
    DEVICE_GEO_COUNTRY_NAME = 'device.geo.country.name'
    DEVICE_ORIENTATION = 'device.orientation'
    DEVICE_COLOR_DEPTH = 'device.color.depth'
    DEVICE_RESOLUTION = 'device.resolution'
    DEVICE_TOUCH = 'device.touch'
    DEVICE_TYPE = 'device.type'
    DEVICE_IP = 'device.ip'
    DEVICE_MODEL = 'device.model'
    DEVICE_BRAND = 'device.brand'
    DEVICE_NAME = 'device.name'
    SOURCE_ID = 'source.id'
    REQUEST = 'request'
    METADATA_DEBUG = 'metadata.debug'
    METADATA_INSTANCE_ID = 'metadata.instance.id'
    METADATA_MERGE = 'metadata.merge'
    METADATA_ERROR = 'metadata.error'
    METADATA_WARNING = 'metadata.warning'
    METADATA_VALID = 'metadata.valid'
    METADATA_PROFILE_LESS = 'metadata.profile.less'
    METADATA_PROCESSED_BY_THIRD_PARTY = 'metadata.processed.by.third.party'
    METADATA_PROCESSED_BY_FLOWS = 'metadata.processed.by.flows'
    METADATA_PROCESSED_BY_RULES = 'metadata.processed.by.rules'
    METADATA_IP = 'metadata.ip'
    METADATA_CHANNEL = 'metadata.channel'
    METADATA_STATUS = 'metadata.status'
    METADATA_TIME_TOTAL_TIME = 'metadata.time.total.time'
    METADATA_TIME_PROCESS_TIME = 'metadata.time.process.time'

    OBJECT = 'object'
    SUBJECT = 'subject'
    VERSION = 'version'
    NAME = 'name'
    TYPE = 'type'
    CONFIG = 'config'
    CONTEXT = 'context'
    PROPERTIES = 'properties'
    TRAITS = 'traits'
    TAGS_VALUES = 'tags.values'
    TAGS_COUNT = 'tags.count'
    JOURNEY_STATE = 'journey.state'

    @staticmethod
    def as_entity(flat_event: 'FlatEvent'):
        if not flat_event:
            return None
        return Entity(id=flat_event['id'])

    @property
    def type(self) -> Optional[str]:
        return self.get('type', None)

    @property
    def properties(self) -> dict:
        return self.get('properties', {})

    @property
    def context(self) -> Optional[str]:
        return self.get('context', {})

    def is_async(self) -> bool:
        return 'config' in self and self['config'].get('async', True)

    def is_valid(self) -> bool:
        return self.get('metadata.valid', True)

    def has(self, value, equal=None) -> bool:
        if equal is None:
            return value in self
        return value in self and self[value] == equal

    def has_not_empty(self, value) -> bool:
        return value in self and self[value] is not None

    def set_if_not_instance(self, field: str, value, instance: type):
        if field not in self or not isinstance(self[field], instance):
            self[field] = value

    @staticmethod
    def new() -> 'FlatEvent':
        now = now_in_utc()
        return FlatEvent({
            "id": str(uuid4()),
            "metadata": {"time": {"create": now, "insert": now}}
        })


class FlatEvents(list):
    def group_by_type(self):
        _indexed_flat_events: Dict[str, List[FlatEvent]] = defaultdict(list)
        for flat_event in self:
            _indexed_flat_events[flat_event.type].append(flat_event)
        return _indexed_flat_events

    def get_event_types(self) -> Generator[str, None, None]:
        for flat_event in self:
            yield flat_event.type

    def get_id_type_and_properties(self) -> Generator[Tuple[str, str, dict], None, None]:
        for flat_event in self:
            yield flat_event.id, flat_event.type, flat_event.properties


class EventDict(dict):
    pass

    @property
    def id(self) -> Optional[str]:
        return self.get('id', None)
