from datetime import datetime
from typing import Optional, Any
from .entity import Entity
from .metadata import Metadata
from .time import Time
from .value_object.storage_info import StorageInfo
from ..service.secrets import encrypt, decrypt


class Resource(Entity):
    type: str
    metadata: Optional[Metadata]
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    config: Optional[dict] = {}
    tags: str = "general"
    enabled: Optional[bool] = True
    consent: bool = False

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'resource',
            Resource
        )


class ResourceRecord(Entity):
    type: str
    metadata: Optional[Metadata]
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    config: Optional[str] = None
    enabled: Optional[bool] = True
    tags: str = "event"
    consent: bool = False

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    @staticmethod
    def encode(resource: Resource) -> 'ResourceRecord':
        return ResourceRecord(
            id=resource.id,
            name=resource.name,
            description=resource.description,
            type=resource.type,
            tags=resource.tags,
            enabled=resource.enabled,
            consent=resource.consent,
            config=encrypt(resource.config)
        )

    def decode(self) -> Resource:
        return Resource(
            id=self.id,
            name=self.name,
            description=self.description,
            type=self.type,
            tags=self.tags,
            enabled=self.enabled,
            consent=self.consent,
            config=decrypt(self.config)
        )

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'resource',
            ResourceRecord
        )
