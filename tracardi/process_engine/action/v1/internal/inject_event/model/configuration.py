from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    event_id: str

    @field_validator("event_id")
    @classmethod
    def event_id_can_not_be_empty(cls, value):
        value = value.strip()
        if len(value) == 0:
            raise ValueError("Event id can not be empty")

        return value
