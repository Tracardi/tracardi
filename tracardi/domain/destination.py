from typing import Optional, List
from pydantic import field_validator, BaseModel
from tracardi.domain.entity import Entity
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.domain.named_entity import NamedEntity
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.secrets import b64_decoder, b64_encoder


class DestinationConfig(BaseModel):
    package: str
    init: dict = {}
    form: dict = {}
    pro:bool = False

    @field_validator("package")
    @classmethod
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
    condition: Optional[str] = ""
    on_profile_change_only: Optional[bool] = True
    resource: Entity
    event_type: NamedEntity
    source: NamedEntity

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty")
        return value

    @field_validator("condition")
    @classmethod
    def is_valid_condition(cls, value):
        if value:
            _condition = Condition()
            try:
                _condition.parse(value)
            except Exception as e:
                raise ValueError("There is an error in the prerequisites field. The condition is incorrect. The system "
                                 "could not parse it. Please see the documentation for the condition syntax.", str(e))

        return value


class DestinationRecord(NamedEntity):
    description: Optional[str] = ""
    destination: str
    enabled: bool = False
    tags: List[str] = []
    mapping: Optional[str] = None
    condition: Optional[str] = ""
    on_profile_change_only: Optional[bool] = True
    resource: Entity
    event_type: NamedEntity
    source: NamedEntity

    @field_validator("destination")
    @classmethod
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
            condition=self.condition,
            on_profile_change_only=self.on_profile_change_only,
            event_type=self.event_type,
            source=self.source
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
            condition=destination.condition,
            on_profile_change_only=destination.on_profile_change_only,
            event_type=destination.event_type,
            source=destination.source
        )

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'destination',
            DestinationRecord
        )
