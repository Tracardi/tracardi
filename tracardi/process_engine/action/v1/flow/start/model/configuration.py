from typing import List
from pydantic import BaseModel

from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    debug: bool = False
    events: List[NamedEntity] = []

    def get_allowed_event_types(self) -> List[str]:
        return [event.id for event in self.events]
