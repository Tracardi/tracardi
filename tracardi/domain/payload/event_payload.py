from zoneinfo import ZoneInfo

from tracardi.common.time.date import now_in_utc

from typing import Optional, Any, Union
from uuid import uuid4

import tracardi.config
from pydantic import BaseModel, field_validator, PrivateAttr

from ..api_instance import ApiInstance
from ..entity import Entity
from ..event import Event
from tracardi.domain.event_session import EventSession
from ..session import Session
from ..time import Time
from tracardi.common.tools.getters import get_entity_id


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

    @staticmethod
    def from_event(event: Event) -> 'EventPayload':
        return EventPayload(type=event.type, properties=event.properties, context=event.context)

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
                      session: Union[Optional[Entity], Optional[Session]],
                      profile: Optional[Entity],
                      profile_less: bool) -> dict:

        event_type = self.type.strip()
        event = Event.dictionary(
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

        # To prevent performance bottleneck do not create full event session
        # event["session"] = self._get_event_session(session)
        event['source']['id'] = source.id if not self._source_id else self._source_id
        event['config'] = self.options
        event['operation']['update'] = False
        event['operation']['new'] = True
        event['tags']['values'] = tuple(self.tags)
        event['tags']['count'] = len(self.tags)

        if isinstance(session, Session):
            try:
                title = self.context['page']['title']
            except KeyError:
                title = None

            try:
                url = self.context['page']['url']
            except KeyError:
                url = None

            try:
                referer = self.context['page']['referer']['host']
            except KeyError:
                referer = None

            event["os"] = session.os
            event["app"] = session.app
            event["device"] = session.device

            event["hit"]['title'] = title
            event["hit"]['url'] = url
            event["hit"]['referer'] = referer
            event["utm"] = session.utm

        return event

    @staticmethod
    def _get_event_session(session: Union[Session, Entity]) -> Optional[EventSession]:
        if session is not None:
            if isinstance(session, Session) and isinstance(session.context, dict):
                tz = session.get_time_zone()
                event_session = EventSession(
                    id=session.id,
                    tz=tz
                )

            else:
                event_session = EventSession(
                    id=session.id
                )

            return event_session

        return None
