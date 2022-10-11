from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    string: str
    delimiter: str

    @validator('string')
    def string_must_not_be_empty(cls, value):
        if len(value.strip()) <= 0:
            raise ValueError('String must not be an empty')
        return value