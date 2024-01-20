from typing import List, Any
from typing import Optional

from tracardi.domain.named_entity import NamedEntityInContext


class EventTypeMetadata(NamedEntityInContext):
    event_type: str
    description: Optional[str] = "No description provided"
    enabled: Optional[bool] = False
    index_schema: Optional[dict] = {}
    journey: Optional[str] = None
    tags: List[str] = []
    build_in: Optional[bool] = False

    def __init__(self, **data: Any):
        if 'event_type' in data:
            data['id'] = data['event_type']
        super().__init__(**data)
