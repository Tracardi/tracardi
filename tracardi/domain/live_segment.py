from typing import Optional
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class LiveSegment(NamedEntity):
    description: Optional[str] = ""
    enabled: bool = True
    workflow: NamedEntity

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'live-segment',
            LiveSegment
        )
