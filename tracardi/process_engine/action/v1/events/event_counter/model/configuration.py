from typing import Union

from pydantic import BaseModel, validator
from pytimeparse import parse


class Configuration(BaseModel):
    event_type: str
    time_span: Union[str, int]

    @validator("time_span")
    def valid_time_span(cls, value):
        parsed_value = parse(value.strip("-"))
        if parsed_value is None:
            raise ValueError("Could not parse {} as time span".format(value))
        return parsed_value

