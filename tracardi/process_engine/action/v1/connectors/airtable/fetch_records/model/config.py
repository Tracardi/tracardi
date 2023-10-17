from pydantic import field_validator, BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Optional
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    base_id: str
    table_name: str
    formula: Optional[str] = None

    @field_validator("base_id")
    @classmethod
    def validate_base_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class APIKey(BaseModel):
    api_key: str
