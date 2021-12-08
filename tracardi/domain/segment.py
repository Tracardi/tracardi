from typing import Optional, Any
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class Segment(NamedEntity):
    description: Optional[str] = ""
    eventType: Optional[str] = None
    condition: str
    enabled: bool = True
    machine_name: str = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.machine_name = self.get_id()

    def get_id(self) -> str:
        return self.name.replace(" ", "-").lower()

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'segment',
            Segment
        )
