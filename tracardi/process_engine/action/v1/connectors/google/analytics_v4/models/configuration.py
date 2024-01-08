from typing import Optional

from pydantic import field_validator

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    name: str
    params: Optional[str] = "{}"

    @field_validator('name')
    @classmethod
    def check_if_category_filled(cls, value):
        if not value:
            raise ValueError("Event name cannot be empty.")
        return value

