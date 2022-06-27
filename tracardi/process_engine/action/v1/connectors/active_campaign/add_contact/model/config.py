from pydantic import BaseModel
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any
from tracardi.domain.entity import Entity


class Config(PluginConfig):
    source: NamedEntity
    fields: Dict[str, Any]


class EndpointConfig(BaseModel):
    source: Entity
