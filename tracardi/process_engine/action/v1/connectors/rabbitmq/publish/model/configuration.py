from typing import Optional

from pydantic import BaseModel, validator
from tracardi.domain.entity import Entity


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


class PluginConfiguration(BaseModel):
    source: Entity
    queue: QueueConfig
