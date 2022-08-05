from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Dict
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    mapping: Dict


class MixPanelCredentials(BaseModel):
    token: str
    server_prefix: str

    @validator("server_prefix")
    def validate_server_prefix(cls, value):
        if value.lower() not in ("us", "eu"):
            raise ValueError("Server prefix value must be either US or EU.")
        return value
