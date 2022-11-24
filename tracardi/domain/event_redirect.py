from typing import Optional, Any, List
from uuid import uuid4

from pydantic import AnyHttpUrl, validator

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.storage_info import StorageInfo


class EventRedirect(NamedEntity):
    description: Optional[str] = ""
    url: AnyHttpUrl
    props: Optional[dict] = {}
    event_type: str
    tags: Optional[List[str]] = []

    def __init__(self, **data: Any):
        if 'id' not in data:
            data['id'] = str(uuid4())
        super().__init__(**data)

    @validator("name")
    def name_is_not_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @validator("event_type")
    def event_type_is_not_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Event type cannot be empty")
        return value

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'event-redirect',
            EventRedirect
        )
