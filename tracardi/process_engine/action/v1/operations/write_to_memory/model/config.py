from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    key: str
    value: str
    ttl: int
