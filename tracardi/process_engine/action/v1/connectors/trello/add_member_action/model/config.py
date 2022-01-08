from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    board_url: str
    list_name: str
    list_id: str = None
    card_name: str
    member_id: str

