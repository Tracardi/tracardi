from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    debug: bool = False
    profile_id: str

    @field_validator("profile_id")
    @classmethod
    def remove_whitespaces_from_event_id(cls, value):
        return value.strip()
