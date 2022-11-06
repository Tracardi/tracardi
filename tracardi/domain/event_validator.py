from tracardi.domain.named_entity import NamedEntity
from typing import Optional, List
from pydantic import BaseModel, validator
import jsonschema
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.secrets import b64_encoder, b64_decoder


class ValidationSchema(BaseModel):
    json_schema: dict
    condition: Optional[str] = None

    @validator("json_schema")
    def validate_schemas_format(cls, v):
        for value in v.values():
            try:
                jsonschema.Draft202012Validator.check_schema(value)
            except jsonschema.SchemaError as e:
                raise ValueError(f"Validation JSON-schema is invalid. Please refer to documentation "
                                 f"for the JSON-schema format. "
                                 f"Error message: {str(e)}")
        return v

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


class EventValidatorRecord(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    validation: str


class EventValidator(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    validation: ValidationSchema

    def encode(self) -> EventValidatorRecord:
        return EventValidatorRecord(
            id=self.id,
            name=self.name,
            event_type=self.event_type,
            description=self.description,
            tags=self.tags,
            validation=b64_encoder(self.validation.dict())
        )

    @staticmethod
    def decode(record: EventValidatorRecord) -> 'EventValidator':
        return EventValidator(
            id=record.id,
            name=record.name,
            event_type=record.event_type,
            description=record.description,
            tags=record.tags,
            validation=ValidationSchema(**b64_decoder(record.validation))
        )
