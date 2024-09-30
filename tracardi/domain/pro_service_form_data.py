from typing import List, Optional

from pydantic import field_validator, BaseModel


class DocumentationMetadata(BaseModel):
    file: str
    path: Optional[str] = None
    url: Optional[str] = None


class ResourceMetadata(BaseModel):
    type: str
    name: str
    description: str
    traffic: str
    icon: str
    tags: List[str] = []
    submit: List[str] = None
    requirements: Optional[dict] = {}
    context: Optional[dict] = {}
    documentation: Optional[DocumentationMetadata] = None

    @field_validator("name")
    @classmethod
    def name_can_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name can not be empty")
        return value


class ProServiceFormMetaData(BaseModel):
    name: str
    description: Optional[str] = None
    tags: List[str] = []

    @field_validator("name")
    @classmethod
    def name_can_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name can not be empty")
        return value


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
    plugins: Optional[List[dict]] = None  # this is Plugin
