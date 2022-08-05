from pydantic import BaseModel, validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    key: str

    @validator("key")
    def must_not_be_empty(cls, value):
        if value == "":
            raise ValueError("This field can not be empty")
        return value
