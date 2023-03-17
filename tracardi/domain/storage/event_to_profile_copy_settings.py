from typing import Optional, List, Generator, Any

from pydantic import BaseModel

from tracardi.domain.event_to_profile import EventToProfileMap


class EventToProfileCopySettings(BaseModel):
    query: Optional[str] = None
    mappings: List[EventToProfileMap] = []

    def is_empty(self) -> bool:
        if not self.mappings:
            return True

        for mapping in self.mappings:
            if not mapping.is_empty():
                return False

        return True

    def get_mappings(self) -> Generator[EventToProfileMap, Any, None]:
        for mapping in self.mappings:
            if mapping.is_empty():
                continue
            yield mapping

