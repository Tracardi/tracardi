from typing import List, Any
from typing import Optional

from tracardi.domain.named_entity import NamedEntity


class EventTypeMetadata(NamedEntity):
    name: str
    event_type: str
    description: Optional[str] = "No description provided"
    tags: List[str] = []

    def __init__(self, **data: Any):
        if 'event_type' in data:
            data['id'] = data['event_type']
        super().__init__(**data)
