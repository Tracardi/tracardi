from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    debug: bool = False
    profile_id: str

    @validator("profile_id")
    def remove_whitespaces_from_event_id(cls, value):
        return value.strip()
