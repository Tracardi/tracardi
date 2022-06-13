from pydantic import BaseModel, validator

from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    event_type: NamedEntity
    offset: int

    @validator("event_type")
    def must_not_be_empty(cls, value):
        if value.id == "":
            raise ValueError("This field can not be empty")
        return value

    @validator("offset")
    def validate_offset(cls, value):
        if not -10 <= value <= 0:
            raise ValueError("Offset must be an integer between -10 and 0 inclusively.")

        return value
