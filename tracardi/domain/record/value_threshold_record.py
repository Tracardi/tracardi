from datetime import datetime
from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class ValueThresholdRecord(NamedEntity):
    profile_id: Optional[str] = None
    timestamp: datetime
    ttl: int
    last_value: str

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'value-threshold',
            ValueThresholdRecord
        )
