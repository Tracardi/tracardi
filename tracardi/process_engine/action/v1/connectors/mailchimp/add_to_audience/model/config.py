from pydantic import validator
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    list_id: str
    email: str
    merge_fields: Dict[str, Any]
    subscribed: bool
    update: bool

    @validator("list_id")
    def validate_list_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("email")
    def validate_email(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

