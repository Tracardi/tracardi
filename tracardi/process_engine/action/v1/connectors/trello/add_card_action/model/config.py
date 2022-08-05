from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Optional, Union
from datetime import datetime
from tracardi.service.plugin.domain.config import PluginConfig


class Card(BaseModel):
    name: str
    desc: Optional[str] = None
    urlSource: Optional[str] = None
    coordinates: Optional[str] = None
    due: Optional[Union[str, datetime]] = None


class Config(PluginConfig):
    source: NamedEntity
    board_url: str
    list_name: str
    list_id: str = None
    card: Card
