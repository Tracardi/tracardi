from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    email: str
