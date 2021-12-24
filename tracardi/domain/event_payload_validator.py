import jsonschema
from pydantic import BaseModel, validator
from typing import Dict
from tracardi.service.secrets import encrypt, decrypt


class EventPayloadValidator(BaseModel):
    validation: Dict[str, Dict]
    event_type: str

    @validator("validation")
    def validate_schemas_format(cls, v):
        for value in v.values():
            try:
                jsonschema.Draft202012Validator.check_schema(value)
            except jsonschema.SchemaError as e:
                raise ValueError(f"Validation schema is invalid, detail: {str(e)}")
        return v

    def encode(self) -> 'EventPayloadValidatorRecord':
        return EventPayloadValidatorRecord(
            validation=encrypt(self.validation),
            id=self.event_type.lower().replace(" ", "-")
        )

    @staticmethod
    def decode(record: 'EventPayloadValidatorRecord') -> 'EventPayloadValidator':
        return EventPayloadValidator(
            validation=decrypt(record.validation),
            event_type=record.id
        )


class EventPayloadValidatorRecord(BaseModel):
    validation: str
    id: str


