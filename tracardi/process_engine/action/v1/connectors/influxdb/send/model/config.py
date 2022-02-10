from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any, List
from typing import Optional


class Config(BaseModel):
    source: NamedEntity
    bucket: str
    fields: Dict[str, Any]
    measurement: str
    time: Optional[str]
    tags: Dict = {}
    organization: str

    @validator("bucket")
    def validate_bucket(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator('measurement')
    def validate_measurement(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class InfluxCredentials(BaseModel):
    url: str
    token: str

