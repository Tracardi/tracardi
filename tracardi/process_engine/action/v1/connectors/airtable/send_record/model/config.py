from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    base_id: str
    table_name: str
    mapping: Dict[str, Any]

    @validator("base_id")
    def validate_base_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("table_name")
    def validate_table_name(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class APIKey(BaseModel):
    api_key: str
