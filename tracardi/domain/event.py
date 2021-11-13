from datetime import datetime
from typing import Optional, Any, List
from uuid import uuid4
from .context import Context
from .entity import Entity
from .metadata import Metadata
from .profile import Profile
from .session import Session
from .time import Time
from pydantic import BaseModel


class Tags(BaseModel):
    content: List[str] = []
    count: int = 0


class Event(Entity):
    metadata: Metadata
    type: str
    properties: Optional[dict] = {}

    source: Entity
    session: Session
    profile: Profile = None
    context: Context
    tags: Tags = Tags(content=[], count=0)

    def __init__(self, **data: Any):
        if 'metadata' in data and isinstance(data['metadata'], Metadata):
            data['metadata'].time = Time(
                insert=datetime.utcnow()
            )
        else:
            data['metadata'] = Metadata(
                time=Time(
                    insert=datetime.utcnow()
                )
            )
        super().__init__(**data)

    def replace(self, event):
        self.id = event.id
        self.type = event.type
        self.properties = event.properties
        self.source = event.source
        self.session = event.session
        self.profile = event.profile
        self.context = event.context

    def is_persistent(self) -> bool:
        if 'save' in self.context.config and isinstance(self.context.config['save'], bool):
            return self.context.config['save']
        else:
            return True


    @staticmethod
    def new(data: dict) -> 'Event':
        data['id'] = str(uuid4())
        return Event(**data)
