from typing import Dict
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    conditions: Dict[str, str]
