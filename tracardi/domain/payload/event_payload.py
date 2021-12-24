from typing import Optional
from uuid import uuid4

from pydantic import BaseModel

from ..context import Context
from ..entity import Entity
from ..event import Event
from ..event_metadata import EventPayloadMetadata, EventMetadata


class EventPayload(BaseModel):
    type: str
    properties: Optional[dict] = {}
    user: Optional[Entity] = None
    options: Optional[dict] = {}

    def to_event(self, metadata: EventPayloadMetadata, source: Entity, session: Entity, profile: Optional[Entity],
                 options: dict, profile_less: bool) -> Event:

        meta = EventMetadata(**metadata.dict())
        meta.profile_less = profile_less

        return Event(id=str(uuid4()),
                     metadata=meta,
                     session=Entity(id=session.id),
                     profile=profile,  # profile can be None when profile_less event.
                     user=self.user,
                     type=self.type,
                     properties=self.properties,
                     source=source,  # Entity
                     context=Context(config=options, params={})
                     )
