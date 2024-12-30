from typing import List, Any
from typing import Optional

from tracardi.domain.named_entity import NamedEntityInContext
from tracardi.common.template.event_description_template import EventDescriptionTemplate


class EventTypeMetadata(NamedEntityInContext):
    event_type: str
    description: Optional[str] = ""
    enabled: Optional[bool] = False
    index_schema: Optional[dict] = {}
    journey: Optional[str] = None
    tags: List[str] = []
    build_in: Optional[bool] = False
    locked: Optional[bool] = False

    def __init__(self, **data: Any):
        if 'event_type' in data:
            data['id'] = data['event_type']
        super().__init__(**data)


    def render_description(self, flat_event) -> Optional[str]:
        if not self.description:
            return None
        template = EventDescriptionTemplate()
        return template.render(self.description, flat_event)
