from typing import Optional, List

from pydantic import validator

from tracardi.domain.value_object.storage_info import StorageInfo

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.secrets import b64_decoder, b64_encoder, encrypt, decrypt


class Destination(NamedEntity):
    description: Optional[str] = ""
    package: str
    enabled: bool = False
    tags: List[str] = []
    mapping: dict = {}
    config: dict = {}

    @validator("name")
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name can not be empty")
        return value

    @validator("package")
    def package_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Destination can not be empty")
        return value


class DestinationRecord(NamedEntity):
    description: Optional[str] = ""
    package: str
    enabled: bool = False
    tags: List[str] = []
    mapping: Optional[str] = None
    config: Optional[str] = None

    def decode(self):
        return Destination(
            id=self.id,
            name=self.name,
            description=self.description,
            package=self.package,
            enabled=self.enabled,
            tags=self.tags,
            mapping=b64_decoder(self.mapping) if self.mapping else {},
            config=decrypt(self.config) if self.config else {}
        )

    @staticmethod
    def encode(destination: Destination):
        return DestinationRecord(
            id=destination.id,
            name=destination.name,
            description=destination.description,
            package=destination.package,
            enabled=destination.enabled,
            tags=destination.tags,
            mapping=b64_encoder(destination.mapping),
            config=encrypt(destination.config)
        )

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'destination',
            DestinationRecord
        )
