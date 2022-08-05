from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    board_url: str
    list_name: str
    list_id: str = None
    card_name: str
    member_id: str

