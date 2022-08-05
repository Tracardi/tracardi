from typing import Optional

from pydantic import AnyHttpUrl
from tracardi.service.plugin.domain.config import PluginConfig


class DiscordWebHookConfiguration(PluginConfig):
    url: AnyHttpUrl
    timeout: int = 10
    message: str
    username: Optional[str] = None

