from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    string: str
    find_regex: str
    replace_with: str

    @field_validator("string")
    @classmethod
    def validate_string_value(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("find_regex")
    @classmethod
    def validate_find_regex(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

