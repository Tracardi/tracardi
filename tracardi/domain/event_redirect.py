from typing import Optional, Any, List
from uuid import uuid4

from pydantic import field_validator

from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext
from tracardi.domain.value_object.storage_info import StorageInfo


class EventRedirect(NamedEntityInContext):
    source: NamedEntity
    description: Optional[str] = ""
    url: str  # AnyHttpUrl
    props: Optional[dict] = {}
    event_type: str
    tags: Optional[List[str]] = []

    def __init__(self, **data: Any):
        if 'id' not in data:
            data['id'] = str(uuid4())

        super().__init__(**data)

    @field_validator("source")
    @classmethod
    def source_is_not_empty(cls, value):
        if not value.id.strip():
            raise ValueError("Source cannot be empty")
        return value

    @field_validator("name")
    @classmethod
    def name_is_not_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("event_type")
    @classmethod
    def event_type_is_not_empty(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Event type cannot be empty")
        return value
