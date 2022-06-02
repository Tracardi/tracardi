from typing import Union

from pydantic import BaseModel, validator
from pytimeparse import parse


class Configuration(BaseModel):
    field: str
    time_span: str

    @validator("field")
    def field_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Field name can not be empty")
        return value

    @validator("time_span")
    def valid_time_span(cls, value):
        if parse(value.strip("-")) is None:
            raise ValueError("Could not parse {} as time span".format(value))
        return value
