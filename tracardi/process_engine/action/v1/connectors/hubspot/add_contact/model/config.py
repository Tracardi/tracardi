from tracardi.domain.named_entity import NamedEntity
from pydantic import BaseModel
from typing import Dict, Any


class Config(BaseModel):
    source: NamedEntity
    properties: Dict[str, Any]


