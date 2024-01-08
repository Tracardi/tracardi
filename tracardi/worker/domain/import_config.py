from typing import Optional

from pydantic import field_validator, BaseModel

from tracardi.worker.domain.named_entity import NamedEntity


class ImportConfig(BaseModel):
    name: str
    description: Optional[str] = ""
    api_url: str  # AnyHttpUrl
    event_source: NamedEntity
    event_type: str
    module: str
    config: dict
    enabled: bool = True
    transitional: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if len(value) == 0:
            raise ValueError("Name cannot be empty.")
        return value

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value):
        if len(value) == 0:
            raise ValueError("Event type cannot be empty.")
        return value
