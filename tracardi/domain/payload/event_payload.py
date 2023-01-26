from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

from pydantic import BaseModel, validator

from ..api_instance import ApiInstance
from ..entity import Entity
from ..event import Event, EventSession, Tags
from ..event_metadata import EventMetadata
from ..event_metadata import EventPayloadMetadata
from ..session import Session, SessionContext
from ..time import Time
from ..value_object.operation import RecordFlag
from ...service.utils.getters import get_entity


class EventPayload(BaseModel):
    time: Optional[Time] = Time()
    type: str
    properties: Optional[dict] = {}
    options: Optional[dict] = {}
    context: Optional[dict] = {}
    tags: Optional[list] = []

    def __init__(self, **data: Any):
        if 'time' not in data or 'insert' not in data['time']:
            data['time'] = Time(insert=datetime.utcnow())
        super().__init__(**data)

    @validator("type")
    def event_type_can_not_be_empty(cls, value):
        value = value.strip()
        if value == "":
            raise ValueError("Event type can not be empty")
        return value

    @staticmethod
    def from_event(event: Event) -> 'EventPayload':
        return EventPayload(type=event.type, properties=event.properties, context=event.context)

    def to_event(self, metadata: EventPayloadMetadata, source: Entity, session: Optional[Session],
                 profile: Optional[Entity],
                 has_profile: bool) -> Event:

        meta = EventMetadata(**metadata.dict())
        meta.profile_less = not has_profile
        meta.instance = Entity(id=ApiInstance().id)

        if self.time.insert:
            meta.time.insert = self.time.insert

        if self.time.create:
            meta.time.create = self.time.create

        return Event(id=str(uuid4()),
                     metadata=meta,
                     session=self._get_event_session(session),
                     profile=get_entity(profile),  # profile can be None when profile_less event.
                     type=self.type.strip(),
                     properties=self.properties,
                     source=source,  # Entity
                     config=self.options,
                     context=self.context,
                     operation=RecordFlag(new=True),
                     tags=Tags(values=tuple(self.tags), count=len(self.tags))
                     )

    @staticmethod
    def _get_event_session(session: Session) -> Optional[EventSession]:
        if session is not None:
            if isinstance(session, Session) and isinstance(session.context, dict):
                session.context = SessionContext(session.context)

                event_session = EventSession(
                    id=session.id,
                    tz=session.context.get_time_zone()
                )

            else:
                event_session = EventSession(
                    id=session.id
                )

            return event_session

        return None
