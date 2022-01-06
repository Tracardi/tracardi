import jsonschema
from pydantic import BaseModel, validator
from typing import Dict, List
from tracardi.service.secrets import encrypt, decrypt
from typing import Optional


class EventPayloadValidator(BaseModel):
    validation: dict
    event_type: str
    name: str
    description: Optional[str] = "No description provided"
    enabled: bool
    tags: List[str] = []

    @validator("validation")
    def validate_schemas_format(cls, v):
        for value in v.values():
            try:
                jsonschema.Draft202012Validator.check_schema(value)
            except jsonschema.SchemaError as e:
                raise ValueError(f"Validation JSON-schema is invalid. Please refer to documentation "
                                 f"for the JSON-schema format. "
                                 f"Error message: {str(e)}")
        return v

    def encode(self) -> 'EventPayloadValidatorRecord':
        return EventPayloadValidatorRecord(
            validation=encrypt(self.validation),
            id=self.event_type.lower().replace(" ", "-"),
            name=self.name,
            description=self.description,
            enabled=self.enabled,
            tags=self.tags
        )

    @staticmethod
    def decode(record: 'EventPayloadValidatorRecord') -> 'EventPayloadValidator':
        return EventPayloadValidator(
            validation=decrypt(record.validation),
            event_type=record.id,
            name=record.name,
            description=record.description,
            enabled=record.enabled,
            tags=record.tags
        )


class EventPayloadValidatorRecord(BaseModel):
    validation: str
    id: str
    name: str
    description: str
    enabled: bool
    tags: List[str]

