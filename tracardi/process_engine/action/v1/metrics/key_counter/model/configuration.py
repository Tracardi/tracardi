from typing import Union, List
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    key: Union[str, List[str]]
    save_in: str
