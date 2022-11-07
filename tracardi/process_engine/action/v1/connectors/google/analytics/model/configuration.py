from typing import Any

from pydantic import validator

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    category: str
    action: str
    label: str
    value: Any


    @validator('category')
    def check_if_category_filled(cls, value):
        if not value:
            raise ValueError("Category field cannot be empty.")
        return value

    @validator('action')
    def check_if_action_filled(cls, value):
        if not value:
            raise ValueError("Action field cannot be empty.")
        return value

