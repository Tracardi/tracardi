from typing import List, Any
from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    type: str = 'select'
    query: str = "SELECT 1"
    data: List[Any] = []
    timeout: int = None

    @validator("query")
    def must_not_be_empty(cls, value):
        if len(value) < 2:
            raise ValueError("Sql must not be empty.")
        return value

    @validator("type")
    def must_have_certain_value(cls, value):
        allowed_values = ['select', 'insert', 'delete', 'call', 'create']
        if value not in allowed_values:
            raise ValueError(f"Allowed values {allowed_values}")
        return value
