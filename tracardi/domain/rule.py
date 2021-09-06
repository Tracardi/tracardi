from datetime import datetime
from typing import Optional, Any
from .metadata import Metadata
from .named_entity import NamedEntity
from .time import Time
from .type import Type
from .value_object.storage_info import StorageInfo


class Rule(NamedEntity):
    event: Type
    flow: NamedEntity

    source: Optional[NamedEntity] = None
    enabled: Optional[bool] = True
    description: Optional[str] = "No description provided"
    properties: Optional[dict] = None
    metadata: Optional[Metadata]

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    # def storage(self) -> StorageCrud:
    #     return StorageCrud("rule", Rule, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'rule',
            Rule
        )
