from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union, Any

from tracardi.domain.entity import Entity, NullableEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class EntityRecordTime(BaseModel):
    insert: Optional[datetime] = None
    create: Optional[datetime] = None
    update: Optional[datetime] = None
    due: Optional[datetime] = None
    expire: Optional[datetime] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.insert is None:
            self.insert = datetime.utcnow()


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
