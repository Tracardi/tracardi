from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    string: str
    to_remove: str

    @field_validator("string")
    @classmethod
    def validate_string_value(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("to_remove")
    @classmethod
    def validate_to_remove(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
