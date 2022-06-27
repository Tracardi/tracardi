from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    string: str
    find_regex: str
    replace_with: str

    @validator("string")
    def validate_string_value(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("find_regex")
    def validate_find_regex(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

