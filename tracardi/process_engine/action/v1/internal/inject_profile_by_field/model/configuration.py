from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    field: str
    value: str

    @field_validator("field")
    @classmethod
    def field_can_not_be_empty(cls, value):
        value = value.strip()
        if value not in ['data.contact.email.main',
                         'data.contact.email.business',
                         'data.contact.email.private',
                         'data.contact.phone.main',
                         'data.contact.phone.mobile',
                         'data.contact.phone.business',
                         'data.contact.app.twitter',
                         'id']:
            raise ValueError("Value is incorrect")

        return value.strip()

    @field_validator("value")
    @classmethod
    def value_can_not_be_empty(cls, value):
        value = value.strip()
        if len(value) == 0:
            raise ValueError("Field can not be empty")

        return value
