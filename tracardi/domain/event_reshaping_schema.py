from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from typing import Optional, List
from pydantic import BaseModel, validator

from tracardi.domain.ref_value import RefValue
from tracardi.process_engine.tql.condition import Condition


class EntityMapping(BaseModel):
    profile: RefValue
    session: RefValue
    event_type: RefValue


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
    mapping: Optional[EntityMapping] = None
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

    def has_mapping(self) -> bool:
        return bool(self.mapping)


class EventReshapingSchema(NamedEntity):
    event_type: str
    event_source: NamedEntity
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    reshaping: ReshapeSchema
    enabled: bool = False
