from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Union


class Revoke(BaseModel):
    revoke: Union[datetime, None] = None

    def set_to_none(self):
        self.revoke = None


class Consents(BaseModel):
    __root__: Dict[str, Revoke]

    @property
    def id(self):
        return list(self.__root__.items()).pop()[0]

    @property
    def content(self):
        return self.__root__

    def __iter__(self):
        for consent in self.__root__.items():
            yield consent

