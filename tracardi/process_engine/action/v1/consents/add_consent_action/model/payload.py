from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Union


class Configuration(BaseModel):
    consents: str


class Revoke(BaseModel):
    revoke: Union[datetime, None] = None


class Consents(BaseModel):
    __root__: Dict[str, Revoke]

    # TODO REMOVE IF NOT IN USE
    @property
    def id(self):
        return list(self.__root__.items()).pop()[0]

    @property
    def content(self):
        return self.__root__

    def __iter__(self):
        for consent in self.__root__.items():
            yield consent

