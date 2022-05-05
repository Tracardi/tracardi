from pydantic import BaseModel, validator
from .entity import Entity
from typing import Optional
from tracardi.service.secrets import encrypt, decrypt


class BatchRecord(BaseModel):
    name: str
    description: Optional[str] = ""
    resource: Entity
    config: str
    enabled: bool = True


class Batch(BaseModel):
    name: str
    description: Optional[str] = ""
    resource: Entity
    config: dict
    enabled: bool = True

    @validator("name")
    def validate_name(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty.")
        return value

    def encode(self) -> BatchRecord:
        return BatchRecord(
            name=self.name,
            description=self.description,
            resource=self.resource,
            config=encrypt(self.config),
            enabled=self.enabled
        )

    @staticmethod
    def decode(record: BatchRecord) -> 'Batch':
        return Batch(
            name=record.name,
            description=record.description,
            resource=record.resource,
            config=decrypt(record.config),
            enabled=record.enabled
        )


