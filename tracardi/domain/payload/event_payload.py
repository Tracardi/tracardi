from typing import Optional
from pydantic import BaseModel

from ..context import Context
from ..entity import Entity
from ..event import Event
from ..event_metadata import EventMetadata


class EventPayload(BaseModel):
    type: str
    properties: Optional[dict] = {}
    user: Optional[Entity] = None
    options: Optional[dict] = {}

    def to_event(self, metadata: EventMetadata, source: Entity, session: Entity, profile: Entity, options: dict) -> Event:
        return Event.new({
            "metadata": metadata,
            "session": Entity(id=session.id),
            "profile": Entity(id=profile.id),
            "user": self.user,
            "type": self.type,
            "properties": self.properties,
            "source": source,  # Entity
            'context': Context(config=options, params={})
        })

