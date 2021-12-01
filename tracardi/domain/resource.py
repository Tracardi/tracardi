from datetime import datetime
from typing import Optional, Any, List, Union, Type

from pydantic import BaseModel

from .entity import Entity
from .metadata import Metadata
from .time import Time
from .value_object.storage_info import StorageInfo
from ..protocol.debuggable import Debuggable
from ..service.secrets import encrypt, decrypt


class ResourceCredentials(BaseModel):
    production: Optional[dict] = {}
    test: Optional[dict] = {}

    def get_credentials(self, plugin: Debuggable, output: Type[BaseModel]):
        if plugin.debug is True:
            return output(**self.test)
        return output(**self.production)


class Resource(Entity):
    type: str
    metadata: Optional[Metadata]
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    credentials: ResourceCredentials
    tags: Union[List[str], str] = ["general"]
    icon: str = None
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
    credentials: Optional[str] = None
    enabled: Optional[bool] = True
    tags: Union[List[str], str] = ["general"]
    icon: str = None
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
            credentials=encrypt(resource.credentials)
        )

    def decode(self) -> Resource:
        if self.credentials is not None:
            decrypted = decrypt(self.credentials)
        else:
            decrypted = {"production": {}, "test": {}}
        return Resource(
            id=self.id,
            name=self.name,
            description=self.description,
            type=self.type,
            tags=self.tags,
            enabled=self.enabled,
            consent=self.consent,
            credentials=ResourceCredentials(**decrypted)
        )

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'resource',
            ResourceRecord
        )
