from typing import List, Any
from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    type: str = 'select'
    query: str = "SELECT 1"
    data: List[Any] = []
    timeout: int = None

    @field_validator("query")
    @classmethod
    def must_not_be_empty(cls, value):
        if len(value) < 2:
            raise ValueError("Sql must not be empty.")
        return value

    @field_validator("type")
    @classmethod
    def must_have_certain_value(cls, value):
        allowed_values = ['select', 'insert', 'delete', 'call', 'create']
        if value not in allowed_values:
            raise ValueError(f"Allowed values {allowed_values}")
        return value
