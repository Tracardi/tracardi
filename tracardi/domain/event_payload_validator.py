from pydantic import BaseModel, validator
from typing import List, Union, Dict
import jsonschema
from tracardi.service.secrets import encrypt, decrypt


class EventPayloadValidator(BaseModel):
    to_validate: Dict[str, Dict]
    event_type: str

    @validator("to_validate")
    def validate_root(cls, v):
        for value in v.values():
            try:
                jsonschema.Draft202012Validator.check_schema(value)
            except jsonschema.SchemaError as e:
                raise ValueError(f"Given schema is invalid, detail: {str(e)}")
        return v

    def encode(self) -> 'PayloadValidatorRecord':
        return PayloadValidatorRecord(
            to_validate=encrypt(self.to_validate),
            id=self.event_type.lower().replace(" ", "-")
        )


class PayloadValidatorRecord(BaseModel):
    to_validate: str
    id: str

    def decode(self) -> EventPayloadValidator:
        return EventPayloadValidator(
            to_validate=decrypt(self.to_validate),
            event_type=self.id
        )

