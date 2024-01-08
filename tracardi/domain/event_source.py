from datetime import datetime
from typing import Optional, Union, List, Any

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.service.utils.date import now_in_utc


class EventSource(NamedEntity):
    type: List[str]
    bridge: NamedEntity
    timestamp: datetime
    description: Optional[str] = "No description provided"
    channel: Optional[str] = ""
    enabled: Optional[bool] = True
    transitional: Optional[bool] = False
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    returns_profile: Optional[bool] = False   # Todo remove - not used
    permanent_profile_id: Optional[bool] = False
    requires_consent: Optional[bool] = False
    manual: Optional[str] = None
    locked: bool = False
    synchronize_profiles: bool = True
    config: Optional[dict] = None

    def __init__(self, **data: Any):
        if 'timestamp' not in data:
            data['timestamp'] = now_in_utc()
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = [data['type']]
        super().__init__(**data)

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'event-source',
            EventSource
        )

    def is_allowed(self, allowed_types) -> bool:
        return bool(set(self.type).intersection(set(allowed_types)))
