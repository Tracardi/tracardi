from datetime import datetime
from typing import Optional, Union, List, Any

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.entity import Entity


class EventSource(Entity):
    type: List[str]
    bridge: NamedEntity
    timestamp: Optional[datetime]
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    channel: Optional[str] = ""
    enabled: Optional[bool] = True
    transitional: Optional[bool] = False
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    permanent_profile_id: Optional[bool] = False
    requires_consent: Optional[bool] = False
    manual: Optional[str] = None
    locked: bool = False
    synchronize_profiles: bool = True
    config: Optional[dict] = None

    def __init__(self, **data: Any):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = [data['type']]
        super().__init__(**data)

    def is_allowed(self, allowed_types) -> bool:
        return bool(set(self.type).intersection(set(allowed_types)))
