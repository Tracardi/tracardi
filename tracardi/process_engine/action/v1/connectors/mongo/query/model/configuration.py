from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resource_id import ResourceId


class MongoConfiguration(BaseModel):
    uri: str
    timeout: int = 5000


class PluginConfiguration(BaseModel):
    source: NamedEntity
    database: NamedEntity
    collection: NamedEntity
    query: str = "{}"


class DatabaseConfig(BaseModel):
    source: ResourceId
    database: NamedEntity


