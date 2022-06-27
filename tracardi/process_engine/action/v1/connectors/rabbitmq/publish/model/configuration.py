from typing import Optional

from pydantic import BaseModel, validator
from tracardi.domain.entity import Entity
from tracardi.service.plugin.domain.config import PluginConfig


class QueueConfig(BaseModel):
    durable: bool = True
    queue_type: str = 'direct'
    routing_key: str
    name: str
    compression: Optional[str] = None
    auto_declare: bool = True
    serializer: str = 'json'

    @validator("name")
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name can not be empty")
        return value

    @validator("compression")
    def validate_compression(cls, value):
        if value == "none":
            return None
        return value


class PluginConfiguration(PluginConfig):
    source: Entity
    queue: QueueConfig
