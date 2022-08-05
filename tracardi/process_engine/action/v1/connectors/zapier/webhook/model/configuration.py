from pydantic import AnyHttpUrl
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    url: AnyHttpUrl
    body: str = "{}"
    timeout: int = 10
