from typing import Optional

from app.domain.named_entity import NamedEntity
from app.service.storage.crud import StorageCrud


class Segment(NamedEntity):
    description: Optional[str] = ""
    eventType: Optional[str] = None
    condition: str
    enabled: bool = True

    def get_id(self):
        return self.name.replace(" ", "-").lower()

    # Persistence

    def storage(self) -> StorageCrud:
        return StorageCrud("segment", Segment, entity=self)
