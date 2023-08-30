from pydantic import field_validator

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    event_type: str
    source: NamedEntity
    event_properties: str = "{}"
    delay: int = 60

    @field_validator("event_type")
    @classmethod
    def validate_query(cls, value):
        if value is None or value == "":
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("delay")
    @classmethod
    def validate_delay(cls, value):
        if value < 15:
            raise ValueError("Delay must be bigger than or equal to 15 seconds.")
        return value
