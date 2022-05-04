from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.entity import Entity
from typing import Dict, Any


class Config(BaseModel):
    source: NamedEntity
    contact_type: str
    fields: Dict[str, Any]


class EndpointConfig(BaseModel):
    source: Entity

