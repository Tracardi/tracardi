from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.dot_notation_validator import is_dot_notation_valid
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    destination: str

    @field_validator("destination")
    @classmethod
    def validate_destination(cls, value):
        if not is_dot_notation_valid(value) or not value.startswith("payload@"):
            raise ValueError("This dot notation is invalid. It should start with 'payload@'")
        return value

