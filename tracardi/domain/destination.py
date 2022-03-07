from typing import Optional, List
from pydantic import validator, BaseModel
from tracardi.domain.entity import Entity
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.secrets import b64_decoder, b64_encoder


class DestinationConfig(BaseModel):
    package: str
    init: dict = {}
    form: dict = {}

    @validator("package")
    def package_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Destination package cannot be empty")
        return value

    def encode(self):
        return b64_encoder(self)

    @staticmethod
    def decode(encoded_string) -> "DestinationConfig":
        return DestinationConfig(
            **b64_decoder(encoded_string)
        )


class Destination(NamedEntity):
    description: Optional[str] = ""
    destination: DestinationConfig
    enabled: bool = False
    tags: List[str] = []
    mapping: dict = {}
    resource: Entity

    @validator("name")
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty")
        return value


class DestinationRecord(NamedEntity):
    description: Optional[str] = ""
    destination: str
    enabled: bool = False
    tags: List[str] = []
    mapping: Optional[str] = None
    resource: Entity

    @validator("destination")
    def destination_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Destination cannot be empty")
        return value

    def decode(self):
        return Destination(
            id=self.id,
            resource=self.resource,
            name=self.name,
            description=self.description,
            destination=DestinationConfig.decode(self.destination) if self.destination is not None else None,
            enabled=self.enabled,
            tags=self.tags,
            mapping=b64_decoder(self.mapping) if self.mapping else {},
        )

    @staticmethod
    def encode(destination: Destination):
        return DestinationRecord(
            id=destination.id,
            resource=destination.resource,
            name=destination.name,
            description=destination.description,
            destination=destination.destination.encode() if destination.destination else None,
            enabled=destination.enabled,
            tags=destination.tags,
            mapping=b64_encoder(destination.mapping),
        )

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'destination',
            DestinationRecord
        )
