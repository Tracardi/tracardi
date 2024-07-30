from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext
from typing import Optional, List
from pydantic import BaseModel


class EventReshapeDefinition(BaseModel):
    properties: Optional[dict] = None
    context: Optional[dict] = None
    session: Optional[dict] = None

    def has_event_reshapes(self) -> bool:
        return bool(self.properties) or bool(self.context)

    def has_session_reshapes(self) -> bool:
        return bool(self.session)


class ReshapeSchema(BaseModel):
    reshape_schema: EventReshapeDefinition


class EventReshapingSchema(NamedEntityInContext):
    event_type: str
    event_source: NamedEntity
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    reshaping: ReshapeSchema
    enabled: bool = False
