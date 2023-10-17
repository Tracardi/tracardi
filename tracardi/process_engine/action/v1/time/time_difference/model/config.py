from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    reference_date: str
    now: str

    @field_validator("now")
    @classmethod
    def validate_now(cls, value):
        if len(value) == 0:
            raise ValueError("Date can not not be empty")
        return value

    @field_validator("reference_date")
    @classmethod
    def validate_reference_date(cls, value):
        if len(value) == 0:
            raise ValueError("Date can not not be empty")
        return value
