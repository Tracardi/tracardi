from typing import Optional, List

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.service.storage.crud import StorageCrud


class ResponseItem(BaseModel):
    index: str
    slices: Optional[List[str]] = None


class Response(Entity):
    data: List[ResponseItem]

    def storage(self) -> StorageCrud:
        return StorageCrud("response", Response, entity=self)
