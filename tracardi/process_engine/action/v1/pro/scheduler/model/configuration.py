from pydantic import BaseModel

from tracardi.domain.entity import Entity


class Configuration(BaseModel):
    source: Entity
    event_type: str
    properties: str = "{}"
    postpone: int
