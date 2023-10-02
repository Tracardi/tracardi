from tracardi.service.plugin.domain.config import PluginConfig
from typing import Optional


class Configuration(PluginConfig):
    string: str
    format: str
    replace_with: str
