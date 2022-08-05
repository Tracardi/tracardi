from datetime import datetime
from typing import Optional, Any, List, Union, Type
from pydantic import BaseModel

from .destination import DestinationConfig
from .entity import Entity
from .value_object.storage_info import StorageInfo
from ..service.secrets import encrypt, decrypt


class ResourceCredentials(BaseModel):
    production: Optional[dict] = {}
    test: Optional[dict] = {}

    def get_credentials(self, plugin, output: Type[BaseModel] = None):
        """
        Returns configuration of resource depending on the state of the executed workflow: test or production.
        """

        if plugin.debug is True:
            return output(**self.test) if output is not None else self.test
        return output(**self.production) if output is not None else self.production


class Resource(Entity):
    type: str
    timestamp: datetime
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    credentials: ResourceCredentials = ResourceCredentials()
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    icon: str = None
    destination: Optional[DestinationConfig] = None
    enabled: Optional[bool] = True

    def __init__(self, **data: Any):
        data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'resource',
            Resource
        )

    def is_destination(self):
        return self.destination is not None


class ResourceRecord(Entity):
    type: str
    timestamp: datetime
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    credentials: Optional[str] = None
    enabled: Optional[bool] = True
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    icon: str = None
    destination: Optional[str] = None

    def __init__(self, **data: Any):
        data['timestamp'] = datetime.utcnow()
        super().__init__(**data)

    @staticmethod
    def encode(resource: Resource) -> 'ResourceRecord':
        return ResourceRecord(
            id=resource.id,
            name=resource.name,
            description=resource.description,
            type=resource.type,
            tags=resource.tags,
            destination=resource.destination.encode() if resource.destination else None,
            groups=resource.groups,
            enabled=resource.enabled,
            icon=resource.icon,
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
            destination=DestinationConfig.decode(self.destination) if self.destination is not None else None,
            groups=self.groups,
            icon=self.icon,
            enabled=self.enabled,
            credentials=ResourceCredentials(**decrypted)
        )

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'resource',
            ResourceRecord
        )

    def is_destination(self):
        return self.destination is not None
