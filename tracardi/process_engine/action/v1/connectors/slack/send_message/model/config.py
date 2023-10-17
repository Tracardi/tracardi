from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    channel: str
    message: str

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
