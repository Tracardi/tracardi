from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    query: str
    timeout: int = 20
