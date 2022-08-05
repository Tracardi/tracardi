from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import List, Optional
from tracardi.service.plugin.domain.register import Form


class DestinationData(BaseModel):
    package: str
    init: Optional[dict] = {}
    form: Optional[Form] = {}


class ResourceSettings(NamedEntity):
    config: dict
    tags: List[str]
    icon: Optional[str] = "plugin"
    destination: Optional[DestinationData] = None
    manual: Optional[str] = None
    pro: Optional[dict] = None

    def dict(self, *args, **kwargs) -> dict:
        return {key: value for key, value in super().dict(*args, **kwargs).items() if value is not None}

