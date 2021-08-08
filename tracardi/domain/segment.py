from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.crud import StorageCrud


class Segment(NamedEntity):
    description: Optional[str] = ""
    eventType: Optional[str] = None
    condition: str
    enabled: bool = True

    def get_id(self) -> str:
        return self.name.replace(" ", "-").lower()

    # Persistence

    def storage(self) -> StorageCrud:
        return StorageCrud("segment", Segment, entity=self)
