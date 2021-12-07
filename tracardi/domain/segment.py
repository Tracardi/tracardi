from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo
from pydantic import root_validator


class Segment(NamedEntity):
    description: Optional[str] = ""
    eventType: Optional[str] = None
    condition: str
    enabled: bool = True

    def get_id(self) -> str:
        return self.name.replace(" ", "-").lower()

    @root_validator
    def machine_name(cls, values):
        values["machine_name"] = values["name"].replace(" ", "-").lower()
        return values

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'segment',
            Segment
        )
