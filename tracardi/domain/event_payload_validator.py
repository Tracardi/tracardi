import jsonschema
from pydantic import BaseModel, validator
from typing import Dict, List
from tracardi.service.secrets import b64_encoder, b64_decoder
from typing import Optional


class ValidationSchema(BaseModel):
    json_schema: dict
    enabled: bool = False

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


class EventTypeManager(BaseModel):
    name: str
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    validation: ValidationSchema

    def encode(self) -> 'EventPayloadValidatorRecord':
        return EventPayloadValidatorRecord(
            validation=b64_encoder(self.validation),  # Encodes whole validation schema
            id=self.event_type.lower().replace(" ", "-"),
            name=self.name,
            description=self.description,
            tags=self.tags
        )

    @staticmethod
    def decode(record: 'EventPayloadValidatorRecord') -> 'EventTypeManager':
        return EventTypeManager(
            validation=ValidationSchema(**b64_decoder(record.validation)),
            event_type=record.id,
            name=record.name,
            description=record.description,
            tags=record.tags
        )


class EventPayloadValidatorRecord(BaseModel):
    validation: str  # Encrypted validation schema
    id: str
    name: str
    description: str
    tags: List[str]
