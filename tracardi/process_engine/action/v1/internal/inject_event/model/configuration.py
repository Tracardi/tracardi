from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    event_id: str

    @validator("event_id")
    def event_id_can_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Event id can not be empty")

        return value
