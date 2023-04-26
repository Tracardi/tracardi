from typing import List
from typing import Optional

from pydantic import BaseModel
from tracardi.domain.ref_value import RefValue

from tracardi.domain.named_entity import NamedEntity


class EventIndexMap(BaseModel):
    property: RefValue
    trait: RefValue

    def is_empty(self) -> bool:
        return not self.property.has_value() or not self.trait.has_value()


class EventIndexing(NamedEntity):
    event_type: NamedEntity
    description: Optional[str] = "No description provided"
    enabled: Optional[bool] = False
    config: Optional[dict] = {}
    event_indexing: Optional[List[EventIndexMap]] = []
    tags: List[str] = []

    def items(self):
        for item in self.event_indexing:
            yield item.property.value, item.trait.value
