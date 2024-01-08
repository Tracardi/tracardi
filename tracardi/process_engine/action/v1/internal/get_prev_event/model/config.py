from pydantic import field_validator

from tracardi.domain.named_entity import NamedEntity

from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    event_type: NamedEntity
    offset: int

    @field_validator("event_type")
    @classmethod
    def must_not_be_empty(cls, value):
        if value.id == "":
            raise ValueError("This field can not be empty")
        return value

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, value):
        if not -10 <= value <= 0:
            raise ValueError("Offset must be an integer between -10 and 0 inclusively.")

        return value
