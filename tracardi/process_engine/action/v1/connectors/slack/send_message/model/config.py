from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    channel: str
    message: str

    @validator("channel")
    def validate_channel(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("message")
    def validate_message(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class Token(BaseModel):
    token: str
