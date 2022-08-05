from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    name: str
    value: str
    ttl: int = 30 * 60
    assign_to_profile: bool = False
