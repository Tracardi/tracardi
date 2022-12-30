from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from typing import Optional, List
from pydantic import BaseModel, validator
from tracardi.process_engine.tql.condition import Condition


class MergeQuery(BaseModel):
    profile: Optional[str] = "{}"
    session: Optional[str] = "{}"
    event_type: Optional[str] = None


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
    query: Optional[MergeQuery] = None
    condition: Optional[str] = None

    @validator("condition")
    def check_if_condition_valid(cls, value):
        if value:
            try:
                condition = Condition()
                condition.parse(value)
            except Exception as _:
                raise ValueError("Condition expression could not be parsed. It seems to be invalid.")
            return value
        else:
            return None

    def has_query(self) -> bool:
        return bool(self.query)


class EventReshapingSchema(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    reshaping: ReshapeSchema
    enabled: bool = False
