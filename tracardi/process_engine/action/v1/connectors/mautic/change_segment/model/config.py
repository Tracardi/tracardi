from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    contact_id: str
    remove_from: str
    add_to: str

    @validator("contact_id")
    def validate_contact_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("remove_from")
    def validate_remove_from(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("add_to")
    def validate_add_to(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
