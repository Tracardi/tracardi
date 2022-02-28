from pydantic import BaseModel, validator
from pytimeparse import parse as parse_time


class Config(BaseModel):
    index: str
    time_range: str
    query: str

    @validator("time_range")
    def validate_time_range(cls, value):
        if parse_time(value) is None:
            raise ValueError("Given time expression is invalid.")
        return value

    @validator("query")
    def validate_query(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty")
        return value
