from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    email: str
    additional_mapping: Dict[str, Any]
    overwrite_with_blank: bool

    @field_validator("email")
    @classmethod
    def validate_email_exists(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

