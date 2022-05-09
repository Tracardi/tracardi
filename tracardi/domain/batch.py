from pydantic import BaseModel, validator
from typing import Optional
from tracardi.service.secrets import encrypt, decrypt
from tracardi.domain.named_entity import NamedEntity


class BatchRecord(NamedEntity):
    description: Optional[str] = ""
    module: str
    config: str
    enabled: bool = True


class Batch(NamedEntity):
    description: Optional[str] = ""
    module: str
    config: dict
    enabled: bool = True

    @validator("name")
    def validate_name(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty.")
        return value

    def encode(self) -> BatchRecord:
        return BatchRecord(
            id=self.id,
            name=self.name,
            description=self.description,
            module=self.module,
            config=encrypt(self.config),
            enabled=self.enabled
        )

    @staticmethod
    def decode(record: BatchRecord) -> 'Batch':
        return Batch(
            id=record.id,
            name=record.name,
            description=record.description,
            module=record.module,
            config=decrypt(record.config),
            enabled=record.enabled
        )


