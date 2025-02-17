from zoneinfo import ZoneInfo

from tracardi.common.time.date import now_in_utc

from typing import Optional, Any, Union
from uuid import uuid4

import tracardi.config
from pydantic import BaseModel, field_validator, PrivateAttr

from ..api_instance import ApiInstance
from ..entity import Entity, DefaultEntity
from ..time import Time
from tracardi.common.tools.getters import get_entity_id
from ...common.tools.string_manager import capitalize_event_type_id


def dictionary(id: str = None,
               type: str = None,
               session_id: str = None,
               profile_id=None,
               properties: dict = None,
               context=None) -> dict:
    if context is None:
        context = {}
    if properties is None:
        properties = {}
    return {
        "id": id,
        "type": type,
        "name": capitalize_event_type_id(type),
        "metadata": {
            "aux": {},
            "time": {
                "insert": None,
                "create": None,
                "update": None,
                "process_time": 0
            },
            "ip": None,
            "status": None,
            "channel": None,
            "processed_by": {
                "rules": [],
                "flows": [],
                "third_party": []
            },
            "profile_less": False,
            "debug": False,
            "valid": True,
            "error": False,
            "warning": False,
            "instance": {
                "id": None
            }
        },
        "utm": {
            "source": None,
            "medium": None,
            "campaign": None,
            "term": None,
            "content": None
        },
        "properties": properties,
        "traits": {},
        "operation": {
            "new": False,
            "update": False
        },
        "source": {
            "id": None,
            "type": [],
            "bridge": {
                "id": None,
                "name": None
            },
            "timestamp": None,
            "name": None,
            "description": None,
            "channel": None,
            "enabled": True,
            "transitional": False,
            "tags": [],
            "groups": [],
            "returns_profile": False,
            "permanent_profile_id": False,
            "requires_consent": False,
            "manual": None,
            "locked": False,
            "synchronize_profiles": True,
            "config": None
        },
        "session": {
            "id": session_id,
            "start": None,
            "duration": 0,
            "tz": "utc"
        },
        "profile": {
            "id": profile_id
        },
        "context": context,
        "request": {},
        "config": {},
        "tags": {
            "values": (),
            "count": 0
        },
        "aux": {},
        "data": {},
        "device": {
            "name": None,
            "brand": None,
            "model": None,
            "type": None,
            "touch": False,
            "ip": None,
            "resolution": None,
            "geo": {
                "country": {
                    "name": None,
                    "code": None
                },
                "city": None,
                "county": None,
                "postal": None,
                "latitude": None,
                "longitude": None
            },
            "color_depth": None,
            "orientation": None
        },
        "os": {
            "name": None,
            "version": None
        },
        "app": {
            "type": None,
            "name": None,
            "version": None,
            "language": None,
            "bot": False,
            "resolution": None
        },
        "hit": {
            "name": None,
            "url": None,
            "referer": None,
            "query": None,
            "category": None
        },
        "journey": {
            "state": None
        }
    }


class ProcessStatus(BaseModel):
    error: bool
    message: Optional[str] = None
    trace: Optional[list] = []


class EventPayload(BaseModel):
    id: Optional[str] = None
    time: Optional[Time] = Time()
    type: str
    properties: Optional[dict] = {}
    options: Optional[dict] = {}
    context: Optional[dict] = {}
    tags: Optional[list] = []
    validation: Optional[ProcessStatus] = None
    reshaping: Optional[ProcessStatus] = None
    error: Optional[ProcessStatus] = None

    _source_id: str = PrivateAttr(None)

    def __init__(self, **data: Any):

        if 'id' not in data:
            data['id'] = str(uuid4())

        _now = now_in_utc()

        if 'time' not in data:
            data['time'] = Time(insert=_now)
        else:
            if isinstance(data['time'], Time):
                if not data['time'].insert:
                    data['time'].insert = _now
            elif isinstance(data['time'], dict):
                if 'insert' not in data['time']:
                    data['time']['insert'] = _now

        super().__init__(**data)

        if 'source_id' in self.options:
            if self.options['source_id'] == tracardi.config.tracardi.internal_source:
                self._source_id = self.options['source_id']
            del (self.options['source_id'])

    @field_validator("type")
    @classmethod
    def event_type_can_not_be_empty(cls, value):
        value = value.strip()
        if value == "":
            raise ValueError("Event type can not be empty")
        return value

    def is_valid(self) -> bool:
        if self.validation is None:
            return True

        return self.validation.error is False

    def is_async(self) -> bool:
        return self.options.get('async', True)

    def get_source_id(self) -> str:
        return self._source_id

    def has_source_id(self) -> bool:
        return bool(self._source_id)

    def to_event_dict(self,
                      source: Entity,
                      session: Optional[Union[DefaultEntity, Entity]],
                      profile: Optional[Entity],
                      profile_less: bool) -> dict:
        # This is only for validation
        event_type = self.type.strip()
        event = dictionary(
            id=str(uuid4()) if not self.id else self.id,
            profile_id=get_entity_id(profile),
            session_id=get_entity_id(session),
            type=event_type,
            properties=self.properties,
            context=self.context)
        event['profile_less'] = profile_less
        event['metadata']['instance']['id'] = ApiInstance().id

        # Get time from event payload
        if self.time.insert:
            event['metadata']['time']['insert'] = self.time.insert
        else:
            event['metadata']['time']['insert'] = now_in_utc()

        if self.time.create:
            event['metadata']['time']['create'] = self.time.create.replace(tzinfo=ZoneInfo("UTC"))

        event['source']['id'] = source.id if not self._source_id else self._source_id
        event['config'] = self.options
        event['operation']['update'] = False
        event['operation']['new'] = True
        event['tags']['values'] = tuple(self.tags)
        event['tags']['count'] = len(self.tags)

        return event
