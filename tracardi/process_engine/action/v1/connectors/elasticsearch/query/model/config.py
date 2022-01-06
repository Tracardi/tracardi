from pydantic import BaseModel, validator
import json

from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    index: str
    query: str

    @validator("index")
    def validate_index(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("query")
    def validate_content(cls, value):
        try:
            if isinstance(value, dict):
                value = json.dumps(value)
            return value

        except json.JSONDecodeError as e:
            raise ValueError(str(e))


class Credentials(BaseModel):
    url: str
    port: int
    scheme: str
    username: str
    password: str
    verify_certs: bool
