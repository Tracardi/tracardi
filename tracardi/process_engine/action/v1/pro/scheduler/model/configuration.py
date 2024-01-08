from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    resource: NamedEntity
    source: NamedEntity
    event_type: str
    properties: str = "{}"
    postpone: int

    @field_validator("event_type")
    @classmethod
    def validate_query(cls, value):
        if value is None or value == "":
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("postpone")
    @classmethod
    def validate_delay(cls, value):
        if value < 5:
            raise ValueError("Delay must be bigger then 5 seconds.")
        return value

