from datetime import datetime
from typing import Optional, Any, Union
from uuid import uuid4

import tracardi.config
from pydantic import BaseModel, field_validator, PrivateAttr

from ..api_instance import ApiInstance
from ..entity import Entity
from ..event import Event, EventSession, Tags
from ..event_metadata import EventMetadata
from ..event_metadata import EventPayloadMetadata
from ..metadata import Hit
from ..session import Session, SessionContext
from ..time import Time
from ..value_object.operation import RecordFlag
from ...service.string_manager import capitalize_event_type_id
from ...service.utils.getters import get_entity, get_entity_id


class EventPayload(BaseModel):
    time: Optional[Time] = Time()
    type: str
    properties: Optional[dict] = {}
    options: Optional[dict] = {}
    context: Optional[dict] = {}
    tags: Optional[list] = []

    _source_id: str = PrivateAttr(None)

    def __init__(self, **data: Any):

        if 'time' not in data:
            data['time'] = Time(insert=datetime.utcnow())
        else:
            if isinstance(data['time'], Time):
                if not data['time'].insert:
                    data['time'].insert = datetime.utcnow()
            elif isinstance(data['time'], dict):
                if 'insert' not in data['time']:
                    data['time']['insert'] = datetime.utcnow()

        super().__init__(**data)

        if 'source_id' in self.options:
            if self.options['source_id'] == tracardi.config.tracardi.internal_source:
                self._source_id = self.options['source_id']
            del(self.options['source_id'])

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

    def to_event_dict(self,
                      source: Entity,
                      session: Union[Optional[Entity], Optional[Session]],
                      profile: Optional[Entity],
                      has_profile: bool) -> dict:

        event_type = self.type.strip()
        event = Event.dictionary(
            id=str(uuid4()),
            profile_id=get_entity_id(profile),
            session_id=get_entity_id(session),
            type=event_type,
            properties=self.properties,
            context=self.context)
        event['profile_less'] = not has_profile
        event['metadata']['instance']['id'] = ApiInstance().id
        if self.time.insert:
            event['metadata']['time']['insert'] = self.time.insert
        else:
            event['metadata']['time']['insert'] = datetime.utcnow()

        if self.time.create:
            event['metadata']['time']['create'] = self.time.create

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

    def to_event(self, metadata: EventPayloadMetadata, source: Entity,
                 session: Union[Optional[Entity], Optional[Session]],
                 profile: Optional[Entity],
                 has_profile: bool) -> Event:

        meta = EventMetadata(**metadata.model_dump())
        meta.profile_less = not has_profile
        meta.instance = Entity(id=ApiInstance().id)

        if self.time.insert:
            meta.time.insert = self.time.insert

        if self.time.create:
            meta.time.create = self.time.create
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

            hit = Hit(
                name=title,
                url=url,
                referer=referer
            )
            event_type = self.type.strip()
            event = Event(id=str(uuid4()),
                          name=capitalize_event_type_id(event_type),
                          metadata=meta,
                          session=self._get_event_session(session),
                          profile=get_entity(profile),  # profile can be None when profile_less event.
                          type=event_type,

                          os=session.os.model_dump(),
                          app=session.app.model_dump(),
                          device=session.device.model_dump(),
                          hit=hit.model_dump(),

                          utm=session.utm,

                          properties=self.properties,
                          source=source if not self._source_id else Entity(id=self._source_id),  # Entity
                          config=self.options,
                          context=self.context,
                          operation=RecordFlag(new=True),
                          tags=Tags(values=tuple(self.tags), count=len(self.tags))
                          )

        else:
            event_type = self.type.strip()
            event = Event(id=str(uuid4()),
                          name=capitalize_event_type_id(event_type),
                          metadata=meta,
                          session=self._get_event_session(session),
                          profile=get_entity(profile),  # profile can be None when profile_less event.
                          type=event_type,
                          properties=self.properties,
                          source=source if not self._source_id else Entity(id=self._source_id),  # Entity
                          config=self.options,
                          context=self.context,
                          operation=RecordFlag(new=True),
                          tags=Tags(values=tuple(self.tags), count=len(self.tags))
                          )

        return event

    @staticmethod
    def _get_event_session(session: Union[Session, Entity]) -> Optional[EventSession]:
        if session is not None:
            if isinstance(session, Session) and isinstance(session.context, dict):
                session.context = SessionContext(session.context)

                tz = session.context.get_time_zone()
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
