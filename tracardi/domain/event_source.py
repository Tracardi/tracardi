from datetime import datetime
from typing import Optional, Union, List, Any
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.domain.entity import Entity


class EventSource(Entity):
    type: str
    timestamp: datetime
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    url: Optional[str] = None
    username: str = ""
    password: str = ""
    enabled: Optional[bool] = True
    tags: Union[List[str], str] = ["general"]
    icon: str = None

    def __init__(self, **data: Any):
        data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'event-source',
            EventSource
        )
