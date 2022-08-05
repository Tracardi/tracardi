from pydantic import BaseModel

from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resource_id import ResourceId


class MongoConfiguration(BaseModel):
    uri: str
    timeout: int = 5000


class PluginConfiguration(PluginConfig):
    source: NamedEntity
    database: NamedEntity
    collection: NamedEntity
    query: str = "{}"


class DatabaseConfig(BaseModel):
    source: ResourceId
    database: NamedEntity


