from tracardi.domain.named_entity import NamedEntity
from pydantic import BaseModel


class Config(BaseModel):
    source: NamedEntity
    contact_id: int
    is_token_got: bool
