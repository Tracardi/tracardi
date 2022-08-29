from typing import List, Optional

from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class TProMicroserviceCredentials(BaseModel):
    url: str
    token: str

    def is_configured(self) -> bool:
        return bool(self.url and self.token)


class TProMicroserviceResource(BaseModel):
    service: NamedEntity
    credentials: Optional[dict] = {}


class ResourceMetadata(BaseModel):
    type: str
    name: str
    description: str
    traffic: str
    icon: str
    tags: List[str]
    submit: List[str] = None


class ProServiceFormMetaData(BaseModel):
    name: str
    description: Optional[str] = None
    tags: List[str] = []


class ProServiceFormData(BaseModel):
    metadata: ProServiceFormMetaData
    data: dict


class ProServicePayload(BaseModel):
    metadata: ResourceMetadata
    form: ProServiceFormData


class ProDestinationPackage(BaseModel):
    form: dict
    init: dict
    package: str


class ProService(BaseModel):
    service: ProServicePayload
    destination: Optional[ProDestinationPackage] = None


class ProMicroService(ProService):
    microservice: Optional[TProMicroserviceResource]
