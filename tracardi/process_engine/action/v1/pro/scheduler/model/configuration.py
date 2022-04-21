from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    event_type: str
    properties: str = "{}"
    postpone: int
