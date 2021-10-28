from typing import Optional
from pydantic import BaseModel

from ..context import Context
from ..entity import Entity
from ..event import Event


class EventPayload(BaseModel):
    type: str
    properties: Optional[dict] = {}
    user: Optional[Entity] = None
    options: Optional[dict] = {}

    def to_event(self, metadata, source, session, profile, options):
        return Event.new({
            "metadata": metadata,
            "session": session,
            "profile": profile.dict(exclude={"operation": ...}),
            "user": self.user,
            "type": self.type,
            "properties": self.properties,
            "source": source,  # Entity
            'context': Context(config=options, params={})
        })

