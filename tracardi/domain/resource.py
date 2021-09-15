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
    origin: str = "event"
    enabled: Optional[bool] = True
    consent: bool = False

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    # # Persistence
    # def storage(self) -> StorageCrud:
    #     return StorageCrud("resource", Resource, entity=self)

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
    origin: str = "event"
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
            origin=resource.origin,
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
            origin=self.origin,
            enabled=self.enabled,
            consent=self.consent,
            config=decrypt(self.config)
        )

    # Persistence
    # def storage(self) -> StorageCrud:
    #     return StorageCrud("resource", Resource, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'resource',
            ResourceRecord
        )
