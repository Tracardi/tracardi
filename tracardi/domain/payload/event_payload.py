from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel

from ..api_instance import ApiInstance
from ..entity import Entity
from ..event import Event, EventSession
from ..event_metadata import EventPayloadMetadata, EventMetadata
from ..session import Session, SessionContext
from ..value_object.operation import RecordFlag
from ...service.utils.getters import get_entity


class EventPayload(BaseModel):
    type: str
    properties: Optional[dict] = {}
    options: Optional[dict] = {}
    context: Optional[dict] = {}

    @staticmethod
    def from_event(event: Event) -> 'EventPayload':
        return EventPayload(type=event.type, properties=event.properties, context=event.context)

    def to_event(self, request: dict, metadata: EventPayloadMetadata, source: Entity, session: Optional[Session],
                 profile: Optional[Entity],
                 has_profile: bool) -> Event:
        meta = EventMetadata(**metadata.dict())
        meta.profile_less = not has_profile
        meta.instance = Entity(id=ApiInstance().id)
        try:
            if request['headers']['x-timestamp'].isnumeric():
                ts = int(request['headers']['x-timestamp'])/1000
                meta.time.create = datetime.fromtimestamp(ts)
        except KeyError:
            pass

        return Event(id=str(uuid4()),
                     metadata=meta,
                     session=self._get_event_session(session),
                     profile=get_entity(profile),  # profile can be None when profile_less event.
                     type=self.type.strip(),
                     properties=self.properties,
                     source=source,  # Entity
                     config=self.options,
                     context=self.context,
                     operation=RecordFlag(new=True)
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
