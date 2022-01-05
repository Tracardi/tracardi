from pydantic import BaseModel, validator
from typing import Dict, Any


class Source(BaseModel):
    name: str
    id: str


class Config(BaseModel):
    source: Source
    list_id: str
    email: str
    merge_fields: Dict[str, Any]
    subscribed: bool
    update: bool

    @validator("list_id")
    def validate_list_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("email")
    def validate_email(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

