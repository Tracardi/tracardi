from tracardi.domain.named_entity import NamedEntity
from typing import Optional, List
from pydantic import BaseModel, validator
import jsonschema
from tracardi.process_engine.tql.condition import Condition


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


class EventValidator(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []
    validation: ValidationSchema

