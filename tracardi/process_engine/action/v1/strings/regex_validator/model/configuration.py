from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    validation_regex: str
    data: str



