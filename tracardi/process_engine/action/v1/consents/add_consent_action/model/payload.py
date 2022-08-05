from pydantic import BaseModel
from typing import Dict
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    consents: str


class Consents(BaseModel):
    __root__: Dict[str, bool]

    def __iter__(self):
        for item in self.__root__.items():
            yield item

