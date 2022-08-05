from pydantic import BaseModel, validator

from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    topic: str
    payload: str
    qos: str = "0"
    retain: bool = False

    @validator("qos")
    def must_be_number(cls, value):
        if not value.isnumeric():
            raise ValueError("Value must be a number.")
        return value
