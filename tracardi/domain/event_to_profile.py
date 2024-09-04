from typing import List, Union, Any
from typing import Optional

from pydantic import BaseModel

from tracardi.domain.operations import APPEND, EQUALS, EQUALS_IF_NOT_EXISTS, UPDATE
from tracardi.domain.ref_value import RefValue

from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext


class EventToProfileMap(BaseModel):
    event: RefValue
    op: int
    profile: RefValue

    def __init__(self, **data: Any):
        if 'op' in data and isinstance(data['op'], str):
            if data['op'] in ['equals', 'equal']:
                data['op'] = EQUALS
            elif data['op'] == 'append':
                data['op'] = APPEND
            elif data['op'] == 'equals_if_not_exists':
                data['op'] = EQUALS_IF_NOT_EXISTS
            elif data['op'] in ['update']:
                data['op'] = UPDATE
            else:
                raise ValueError(f"Unknown operation in event to profile mapping. Expected: equals, append, or equals_if_not_exists, got: {data['op']}")

        super().__init__(**data)


    def is_empty(self) -> bool:
        return not self.event.has_value() or not self.profile.has_value()


class EventToProfile(NamedEntityInContext):
    event_type: NamedEntity
    description: Optional[str] = "No description provided"
    enabled: Optional[bool] = False
    config: Optional[dict] = {}
    event_to_profile: Optional[List[EventToProfileMap]] = []
    tags: List[str] = []
    build_in: Optional[bool] = False


    def items(self):
        for item in self.event_to_profile:
            yield item.event.value, item.profile.value, item.op
