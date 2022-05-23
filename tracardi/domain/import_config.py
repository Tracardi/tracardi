from pydantic import BaseModel, validator, AnyHttpUrl
from typing import Optional
from tracardi.service.secrets import encrypt, decrypt
from tracardi.domain.named_entity import NamedEntity


class ImportConfigRecord(NamedEntity):
    description: Optional[str] = ""
    api_url: AnyHttpUrl
    event_source: NamedEntity
    event_type: str
    module: str
    config: str
    enabled: bool = True


class ImportConfig(NamedEntity):
    description: Optional[str] = ""
    module: str
    config: dict
    enabled: bool = True
    api_url: AnyHttpUrl
    event_source: NamedEntity
    event_type: str

    @validator("name")
    def validate_name(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty.")
        return value

    @validator("event_type")
    def validate_event_type(cls, value):
        if len(value) == 0:
            raise ValueError("Event type cannot be empty.")
        return value

    def encode(self) -> ImportConfigRecord:
        return ImportConfigRecord(
            id=self.id,
            name=self.name,
            description=self.description,
            event_type=self.event_type,
            event_source=self.event_source,
            api_url=self.api_url,
            module=self.module,
            config=encrypt(self.config),
            enabled=self.enabled,
        )

    @staticmethod
    def decode(record: ImportConfigRecord) -> 'ImportConfig':
        return ImportConfig(
            id=record.id,
            name=record.name,
            description=record.description,
            api_url=record.api_url,
            event_source=record.event_source,
            event_type=record.event_type,
            module=record.module,
            config=decrypt(record.config),
            enabled=record.enabled,
        )


