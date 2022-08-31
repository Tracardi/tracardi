from pydantic import BaseModel

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    email: str


class Token(BaseModel):
    token: str
