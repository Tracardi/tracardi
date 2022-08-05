from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    xpath: str
    content: str
