from tracardi.domain.named_entity import NamedEntity
from typing import Optional, List
from pydantic import BaseModel, validator
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.secrets import b64_encoder, b64_decoder


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
                raise ValueError("Given condition expression is invalid.")
            return value
        else:
            return None


class EventReshapingSchemaRecord(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    reshaping: str


class EventReshapingSchema(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    reshaping: ReshapeSchema

    def encode(self) -> EventReshapingSchemaRecord:
        return EventReshapingSchemaRecord(
            id=self.id,
            name=self.name,
            event_type=self.event_type,
            description=self.description,
            tags=self.tags,
            reshaping=b64_encoder(self.reshaping.dict())
        )

    @staticmethod
    def decode(record: EventReshapingSchemaRecord) -> 'EventReshapingSchema':
        return EventReshapingSchema(
            id=record.id,
            name=record.name,
            event_type=record.event_type,
            description=record.description,
            tags=record.tags,
            reshaping=ReshapeSchema(**b64_decoder(record.reshaping))
        )
