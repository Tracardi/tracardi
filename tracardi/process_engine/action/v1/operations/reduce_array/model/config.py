from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    array: str

    @field_validator("array")
    @classmethod
    def validate_array(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
