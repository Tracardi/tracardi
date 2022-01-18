from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Dict


class Config(BaseModel):
    source: NamedEntity
    organization: str
    bucket: str
    filters: Dict
    start: str
    stop: str


class InfluxCredentials(BaseModel):
    url: str
    token: str
