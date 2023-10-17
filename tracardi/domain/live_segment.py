from datetime import datetime
from typing import Optional
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class LiveSegment(NamedEntity):
    timestamp: Optional[datetime] = None
    description: Optional[str] = ""
    enabled: bool = True
    workflow: NamedEntity
    type: Optional[str] = 'workflow'

    operation: Optional[str] = None
    condition: Optional[str] = None
    segment: Optional[str] = None
    code: Optional[str] = None

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'live-segment',
            LiveSegment
        )
