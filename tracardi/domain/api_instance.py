from tracardi.domain.value_object.storage_info import StorageInfo

from tracardi.domain.entity import Entity
from datetime import datetime


class ApiInstance(Entity):
    ip: str = None
    timestamp: datetime = datetime.utcnow()

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'api-instance',
            ApiInstance
        )