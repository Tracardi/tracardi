from pydantic import field_validator, BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any
from typing import Optional


class Config(BaseModel):
    source: NamedEntity
    bucket: str
    fields: Dict[str, Any]
    measurement: str
    time: Optional[str] = None
    tags: Dict = {}
    organization: str

    @field_validator("bucket")
    @classmethod
    def validate_bucket(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator('measurement')
    @classmethod
    def validate_measurement(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class InfluxCredentials(BaseModel):
    url: str
    token: str

