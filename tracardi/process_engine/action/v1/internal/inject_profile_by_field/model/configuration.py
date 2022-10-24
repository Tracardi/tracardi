from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    field: str
    value: str

    @validator("field")
    def field_can_not_be_empty(cls, value):
        if value not in ['pii.email', 'pii.telephone', 'pii.twitter']:
            raise ValueError("Value is incorrect")

        return value

    @validator("value")
    def value_can_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Field can not be empty")

        return value
