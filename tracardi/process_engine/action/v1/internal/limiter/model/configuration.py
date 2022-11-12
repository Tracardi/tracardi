from typing import List

from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    keys: List[str]
    limit: int = 1
    ttl: int = 60
