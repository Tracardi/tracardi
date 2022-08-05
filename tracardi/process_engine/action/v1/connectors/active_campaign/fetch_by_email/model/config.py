from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity


class Config(PluginConfig):
    source: NamedEntity
    email: str
