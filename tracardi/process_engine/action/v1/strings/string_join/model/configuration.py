from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    string: str
    delimiter: str

    @field_validator('string')
    @classmethod
    def string_must_not_be_empty(cls, value):
        if len(value.strip()) <= 0:
            raise ValueError('String must not be empty')
        return value

    @field_validator('delimiter')
    @classmethod
    def delimiter_must_be_single_character(cls, value):
        if len(value) != 1:
            raise ValueError('Delimiter must be a single character')
        return value