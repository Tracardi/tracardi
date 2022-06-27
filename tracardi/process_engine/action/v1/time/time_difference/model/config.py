from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    reference_date: str
    now: str

    @validator("now")
    def validate_now(cls, value):
        if len(value) == 0:
            raise ValueError(f"Date can not not be empty")
        return value

    @validator("reference_date")
    def validate_reference_date(cls, value):
        if len(value) == 0:
            raise ValueError(f"Date can not not be empty")
        return value
