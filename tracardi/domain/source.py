from datetime import datetime
from typing import Optional, Any
from .entity import Entity
from tracardi.service.storage.crud import StorageCrud
from .metadata import Metadata
from .time import Time
from ..service.secrets import encrypt, decrypt


class Source(Entity):
    type: str
    metadata: Optional[Metadata]
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    config: Optional[dict] = {}
    origin: str = "event"
    enabled: Optional[bool] = True
    consent: bool = False

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    # Persistence
    def storage(self) -> StorageCrud:
        return StorageCrud("source", Source, entity=self)


class SourceRecord(Entity):
    type: str
    metadata: Optional[Metadata]
    name: Optional[str] = "No name provided"
    description: Optional[str] = "No description provided"
    config: Optional[str] = None
    enabled: Optional[bool] = True
    origin: str = "event"
    consent: bool = False

    def __init__(self, **data: Any):
        data['metadata'] = Metadata(
            time=Time(
                insert=datetime.utcnow()
            ))
        super().__init__(**data)

    @staticmethod
    def encode(source: Source) -> 'SourceRecord':
        return SourceRecord(
            id=source.id,
            name=source.name,
            description=source.description,
            type=source.type,
            origin=source.origin,
            enabled=source.enabled,
            consent=source.consent,
            config=encrypt(source.config)
        )

    def decode(self) -> Source:
        return Source(
            id=self.id,
            name=self.name,
            description=self.description,
            type=self.type,
            origin=self.origin,
            enabled=self.enabled,
            consent=self.consent,
            config=decrypt(self.config)
        )

    # Persistence
    def storage(self) -> StorageCrud:
        return StorageCrud("source", Source, entity=self)
