from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    contact_id: str
    points: str

    @validator("contact_id")
    def validate_contact_id(cls, value):
        if value is None or len(value) == 0:
            print(value)
            raise ValueError("This field cannot be empty.")
        return value

    @validator("points")
    def validate_points(cls, value):
        if value is None or len(value) == 0 or not value.isnumeric():
            print(value)
            raise ValueError("This field must contain an integer.")
        return value
