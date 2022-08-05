from pydantic import BaseModel, validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    array: str

    @validator("array")
    def validate_array(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
