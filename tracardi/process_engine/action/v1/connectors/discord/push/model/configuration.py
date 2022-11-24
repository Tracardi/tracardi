from typing import Optional


from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class DiscordWebHookConfiguration(PluginConfig):
    source: NamedEntity
    timeout: int = 10
    message: str
    username: Optional[str] = None

