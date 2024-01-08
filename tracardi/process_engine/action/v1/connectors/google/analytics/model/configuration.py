from typing import Any

from pydantic import field_validator

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    category: str
    action: str
    label: str
    value: Any = None


    @field_validator('category')
    @classmethod
    def check_if_category_filled(cls, value):
        if not value:
            raise ValueError("Category field cannot be empty.")
        return value

    @field_validator('action')
    @classmethod
    def check_if_action_filled(cls, value):
        if not value:
            raise ValueError("Action field cannot be empty.")
        return value

