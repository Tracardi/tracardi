from tracardi.domain.named_entity import NamedEntity
from typing import Optional, List
from pydantic import field_validator, BaseModel

from tracardi.process_engine.tql.condition import Condition


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


class EventReshapingSchema(NamedEntity):
    event_type: str
    event_source: NamedEntity
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    reshaping: ReshapeSchema
    enabled: bool = False
