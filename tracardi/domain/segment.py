from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class Segment(NamedEntity):
    description: Optional[str] = ""
    eventType: Optional[str] = None
    condition: str
    enabled: bool = True

    def get_id(self) -> str:
        return self.name.replace(" ", "-").lower()

    # Persistence

    # def storage(self) -> StorageCrud:
    #     return StorageCrud("segment", Segment, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'segment',
            Segment
        )
