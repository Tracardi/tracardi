from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class Config(BaseModel):
    source: NamedEntity
    board_url: str
    list_name1: str
    list_id1: str = None
    list_name2: str
    list_id2: str = None
    card_name: str

