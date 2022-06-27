from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    event_type: str
    event_properties: str = "{}"
    delay: int = 60

    @validator("event_type")
    def validate_query(cls, value):
        if value is None or value == "":
            raise ValueError("This field cannot be empty")
        return value

    @validator("delay")
    def validate_delay(cls, value):
        if value < 15:
            raise ValueError("Delay must be bigger than or equal to 15 seconds.")
        return value
