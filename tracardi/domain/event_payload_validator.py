from pydantic import BaseModel, root_validator
from typing import List, Union, Dict
import jsonschema
from tracardi.service.secrets import encrypt, decrypt


class EventPayloadValidator(BaseModel):
    to_exclude: Union[List[str], str]
    to_validate: Dict[str, Dict]
    event_type: str

    @root_validator
    def validate_root(cls, values):
        for value in values["to_validate"].values():
            try:
                jsonschema.Draft202012Validator.check_schema(value)
            except jsonschema.SchemaError as e:
                raise ValueError(f"Given schema is invalid, detail: {str(e)}")
        return values

    def encode(self) -> 'PayloadValidatorRecord':
        return PayloadValidatorRecord(
            to_exclude=self.to_exclude,
            to_validate=encrypt(self.to_validate),
            id=self.event_type.lower().replace(" ", "-")
        )


class PayloadValidatorRecord(BaseModel):
    to_exclude: Union[List[str], str]
    to_validate: str
    id: str

    def decode(self) -> EventPayloadValidator:
        return EventPayloadValidator(
            to_exclude=self.to_exclude,
            to_validate=decrypt(self.to_validate),
            event_type=self.id
        )

