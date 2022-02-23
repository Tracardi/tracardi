from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    text: str
    model: str

    @validator("text")
    def validate_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class Token(BaseModel):
    token: str
