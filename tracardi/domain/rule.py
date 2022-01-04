from datetime import datetime
from typing import Optional, Any, List

from pydantic import validator

from .metadata import Metadata
from .named_entity import NamedEntity
from .time import Time
from .type import Type
from .value_object.storage_info import StorageInfo


class Rule(NamedEntity):
    event: Type
    flow: NamedEntity
    source: NamedEntity
    enabled: Optional[bool] = True
    description: Optional[str] = "No description provided"
    properties: Optional[dict] = None
    metadata: Optional[Metadata]
    tags: Optional[List[str]] = ["General"]

    @validator("tags")
    def tags_can_not_be_empty(cls, value):
        if len(value) == 0:
            value = ["General"]
        return value

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'rule',
            Rule
        )
