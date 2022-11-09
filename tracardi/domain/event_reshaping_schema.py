from tracardi.domain.named_entity import NamedEntity
from typing import Optional, List
from pydantic import BaseModel, validator
from tracardi.process_engine.tql.condition import Condition


class ReshapeSchema(BaseModel):
    reshape_schema: dict
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


class EventReshapingSchema(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    reshaping: ReshapeSchema
    enabled: bool = False
