from typing import Optional

from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    message: str
    timeout: Optional[float] = 15.

    @field_validator("message")
    @classmethod
    def must_not_be_empty(cls, value):
        if len(value) < 2:
            raise ValueError("Message must not be empty.")
        return value
