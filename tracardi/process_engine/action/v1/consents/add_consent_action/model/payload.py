from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Union


class Configuration(BaseModel):
    consents: str


class Consents(BaseModel):
    __root__: Dict[str, bool]

    def __iter__(self):
        for item in self.__root__.items():
            yield item

