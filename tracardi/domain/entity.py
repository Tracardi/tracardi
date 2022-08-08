from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, PrivateAttr

from tracardi.domain.storage_result import RecordMetadata
from tracardi.domain.value_object.storage_info import StorageInfo


class NullableEntity(BaseModel):
    id: Optional[str] = None


class Entity(BaseModel):
    id: str
    _metadata: Optional[RecordMetadata] = PrivateAttr(None)

    def set_meta_data(self, metadata: RecordMetadata):
        self._metadata = metadata

    def get_meta_data(self) -> Optional[RecordMetadata]:
        return self._metadata if isinstance(self._metadata, RecordMetadata) else None

    @staticmethod
    def new() -> 'Entity':
        return Entity(id=str(uuid4()))

    @staticmethod
    def storage_info() -> Optional[StorageInfo]:
        return None
