from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    field: str
    value: str

    @validator("field")
    def field_can_not_be_empty(cls, value):
        value = value.strip()
        if value not in ['data.contact.email', 'data.contact.telephone', 'data.contact.app.twitter', 'id']:
            raise ValueError("Value is incorrect")

        return value.strip()

    @validator("value")
    def value_can_not_be_empty(cls, value):
        value = value.strip()
        if len(value) == 0:
            raise ValueError("Field can not be empty")

        return value
