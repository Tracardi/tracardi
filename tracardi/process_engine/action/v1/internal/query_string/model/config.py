from pydantic import field_validator
from pytimeparse import parse as parse_time
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    index: str
    time_range: str
    query: str = ""

    @field_validator("time_range")
    @classmethod
    def validate_time_range(cls, value):
        if parse_time(value) is None:
            raise ValueError("Given time expression is invalid.")
        return value

    @field_validator("query")
    @classmethod
    def validate_query(cls, value):
        if value is None:
            raise ValueError("This field cannot be empty")
        return value
