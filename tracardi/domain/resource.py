from datetime import datetime
from typing import Optional, Any, List, Union, Type, TypeVar
from uuid import uuid4

from pydantic import BaseModel

from .destination import DestinationConfig
from .entity import Entity
from .named_entity import NamedEntityInContext
from .pro_service_form_data import ProService
from ..context import get_context
from ..service.secrets import encrypt, decrypt
from ..service.utils.date import now_in_utc

T = TypeVar("T")


class ResourceCredentials(BaseModel):
    production: Optional[dict] = {}
    test: Optional[dict] = {}

    def get_credentials(self, plugin, output: Type[T] = None) -> Union[T, dict]:
        """
        Returns configuration of resource depending on the state of the executed workflow: test or production.
        """

        if plugin.debug is True or not get_context().production:
            return output(**self.test) if output is not None else self.test
        return self.get_production_credentials(output)

    def get_production_credentials(self, output: Type[T] = None) -> Union[T, dict]:
        return output(**self.production) if output is not None else self.production


class Resource(NamedEntityInContext):
    type: str
    timestamp: Optional[datetime] = None
    description: Optional[str] = "No description provided"
    credentials: ResourceCredentials = ResourceCredentials()
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    icon: Optional[str] = None
    destination: Optional[DestinationConfig] = None
    enabled: Optional[bool] = True
    locked: Optional[bool] = False

    def __init__(self, **data: Any):
        data['timestamp'] = now_in_utc()
        super().__init__(**data)

    def is_destination(self):
        return self.destination is not None

    def is_destination_pro(self) -> bool:
        return self.destination and self.destination.pro

    @staticmethod
    def from_pro_service(pro: ProService) -> 'Resource':
        return Resource(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            type=pro.service.metadata.type,
            name=pro.service.form.metadata.name or "No name provided",
            description=pro.service.form.metadata.description or "No description provided",
            icon=pro.service.metadata.icon,
            tags=pro.service.form.metadata.tags,
            groups=[],
            credentials=ResourceCredentials(
                test=pro.service.form.data,
                production=pro.service.form.data
            ),
            destination=DestinationConfig(**pro.destination.model_dump()) if pro.destination is not None else None
        )


class ResourceRecord(Entity):
    type: str
    timestamp: datetime
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    credentials: Optional[str] = None
    enabled: Optional[bool] = True
    tags: Union[List[str], str] = ["general"]
    groups: Union[List[str], str] = []
    icon: Optional[str] = None
    destination: Optional[str] = None

    def __init__(self, **data: Any):
        data['timestamp'] = now_in_utc()
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

    def is_destination(self):
        return self.destination is not None
