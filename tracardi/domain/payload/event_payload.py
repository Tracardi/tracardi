from typing import Optional
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
                 options: dict) -> Event:
        return Event.new({
            "metadata": EventMetadata(**metadata.dict()),
            "session": Entity(id=session.id),
            "profile": profile,  # profile can be None when profile_less event.
            "user": self.user,
            "type": self.type,
            "properties": self.properties,
            "source": source,  # Entity
            'context': Context(config=options, params={})
        })

