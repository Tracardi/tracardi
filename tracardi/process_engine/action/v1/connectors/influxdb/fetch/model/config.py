from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Optional


class Config(BaseModel):
    source: NamedEntity
    organization: str
    bucket: str
    filters: Dict
    aggregation: Optional[str] = None
    start: str
    stop: str


class InfluxCredentials(BaseModel):
    url: str
    token: str
