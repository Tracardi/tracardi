from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    list_id: NamedEntity
    email: str
    merge_fields: Dict[str, Any]
    subscribed: bool
    update: bool

    @field_validator("list_id")
    @classmethod
    def validate_list_id(cls, value):
        if value is None or len(value.id) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

