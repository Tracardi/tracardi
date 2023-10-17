from typing import Optional
from pydantic import field_validator, BaseModel


class QueueConfig(BaseModel):
    durable: bool = True
    queue_type: str = 'direct'
    routing_key: str
    name: str
    compression: Optional[str] = None
    auto_declare: bool = True
    serializer: str = 'json'

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name can not be empty")
        return value
