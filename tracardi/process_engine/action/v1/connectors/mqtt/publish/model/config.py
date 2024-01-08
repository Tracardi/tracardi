from pydantic import field_validator, BaseModel

from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    topic: str
    payload: str
    qos: str = "0"
    retain: bool = False

    @field_validator("qos")
    @classmethod
    def must_be_number(cls, value):
        if not value.isnumeric():
            raise ValueError("Value must be a number.")
        return value
