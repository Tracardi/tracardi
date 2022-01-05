import json
from json import JSONDecodeError
from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class MongoConfiguration(BaseModel):
    uri: str
    timeout: int = 5000


class PluginConfiguration(BaseModel):
    source: NamedEntity
    database: str
    collection: str
    query: str = "{}"
