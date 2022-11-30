from datetime import datetime
from typing import Optional, Union, List, Any

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.domain.entity import Entity
from tracardi.service.plugin.domain.register import Form


class EventSource(Entity):
    type: str
    bridge: Optional[NamedEntity] = NamedEntity(id="1", name="API")
    timestamp: datetime
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    enabled: Optional[bool] = True
    transitional: Optional[bool] = False
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    returns_profile: Optional[bool] = False
    permanent_profile_id: Optional[bool] = False
    requires_consent: Optional[bool] = False
    manual: Optional[str] = None
    locked: bool = False
    synchronize_profiles: bool = True
    config: Optional[dict] = None
    form: Optional[Form] = None

    def __init__(self, **data: Any):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'event-source',
            EventSource
        )
