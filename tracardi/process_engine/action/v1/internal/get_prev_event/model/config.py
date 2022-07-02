from pydantic import validator

from tracardi.domain.named_entity import NamedEntity

from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    event_type: NamedEntity
    offset: int

    @validator("event_type")
    def must_not_be_empty(cls, value):
        if value.id == "":
            raise ValueError("This field can not be empty")
        return value

    @validator("offset")
    def validate_offset(cls, value):
        if not -10 <= value <= 0:
            raise ValueError("Offset must be an integer between -10 and 0 inclusively.")

        return value
