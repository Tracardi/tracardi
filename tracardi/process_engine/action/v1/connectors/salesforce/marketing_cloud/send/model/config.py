from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any


class Config(BaseModel):
    source: NamedEntity
    extension_id: str
    update: bool
    mapping: Dict[str, Any]
