from typing import Optional

from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    message: str
    timeout: Optional[float] = 15

    @validator("message")
    def must_not_be_empty(cls, value):
        if len(value) < 2:
            raise ValueError("Message must not be empty.")
        return value
