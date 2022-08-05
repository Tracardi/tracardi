from typing import Optional
from uuid import uuid4
from pydantic import BaseModel
from tracardi.domain.value_object.storage_info import StorageInfo


class NullableEntity(BaseModel):
    id: Optional[str] = None


class Entity(BaseModel):
    id: str

    @staticmethod
    def new() -> 'Entity':
        return Entity(id=str(uuid4()))

    @staticmethod
    def storage_info() -> Optional[StorageInfo]:
        return None
