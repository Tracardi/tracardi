from typing import Optional

from app.domain.named_entity import NamedEntity
from app.service.storage.crud import StorageCrud


class Segment(NamedEntity):
    description: Optional[str] = ""
    condition: str
    enabled: bool = True

    # Persistence

    def storage(self) -> StorageCrud:
        return StorageCrud("segment", Segment, entity=self)
