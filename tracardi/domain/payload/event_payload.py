from typing import Optional
from uuid import uuid4

from pydantic import BaseModel

from ..api_instance import ApiInstance
from ..entity import Entity
from ..event import Event
from ..event_metadata import EventPayloadMetadata, EventMetadata


class EventPayload(BaseModel):
    type: str
    properties: Optional[dict] = {}
    options: Optional[dict] = {}
    context: Optional[dict] = {}

    def to_event(self, metadata: EventPayloadMetadata, source: Entity, session: Optional[Entity], profile: Optional[Entity],
                 has_profile: bool) -> Event:

        meta = EventMetadata(**metadata.dict())
        meta.profile_less = not has_profile
        meta.instance = Entity(id=ApiInstance().id)

        return Event(id=str(uuid4()),
                     metadata=meta,
                     session=Entity(id=session.id) if session is not None else None,
                     profile=profile,  # profile can be None when profile_less event.
                     type=self.type,
                     properties=self.properties,
                     source=source,  # Entity
                     config=self.options,
                     context=self.context
                     )
