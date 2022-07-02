from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    pattern: str
    text: str
    group_prefix: str = "Group"
