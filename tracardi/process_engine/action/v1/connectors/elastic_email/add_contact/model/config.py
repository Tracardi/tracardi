from typing import Dict, Any

from pydantic import field_validator, BaseModel
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    email: str
    additional_mapping: Dict[str, Any]

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class Connection(BaseModel):
    api_key: str
    public_account_id: str
