from datetime import datetime
from typing import Optional, Union

from tracardi.domain.entity import Entity, NullableEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class EntityRecord(Entity):
    id: str
    profile: Union[Entity, NullableEntity]
    timestamp: datetime
    type: str
    properties: Optional[dict] = {}
    traits: Optional[dict] = {}

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'entity',
            EntityRecord
        )
