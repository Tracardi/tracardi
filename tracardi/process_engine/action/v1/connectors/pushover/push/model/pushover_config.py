from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class PushOverAuth(BaseModel):
    token: str
    user: str


class PushOverConfiguration(BaseModel):
    source: NamedEntity
    message: str

    @validator("message")
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Message can not be empty.")
        return value
