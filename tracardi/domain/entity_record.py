from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union

from tracardi.domain.entity import Entity, NullableEntity
from tracardi.domain.time import Time
from tracardi.domain.value_object.storage_info import StorageInfo


class EntityRecordTime(Time):
    due: Optional[datetime] = None
    expire: Optional[datetime] = None


class EntityRecordMetadata(BaseModel):
    time: EntityRecordTime = EntityRecordTime()


class EntityRecord(Entity):
    id: str
    profile: Union[Entity, NullableEntity]
    metadata: Optional[EntityRecordMetadata] = EntityRecordMetadata()
    type: str
    properties: Optional[dict] = {}
    traits: Optional[dict] = {}

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'entity',
            EntityRecord
        )
