from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    reference_date: str
    sign: str
    delay: str

    @field_validator("reference_date")
    @classmethod
    def validate_reference_date(cls, value):
        if len(value.strip()) == 0:
            raise ValueError("Date can not not be empty")
        return value

    @field_validator("sign")
    @classmethod
    def available_values(cls, value):
        value = value.strip()
        if value not in ['+', "-"]:
            raise ValueError("Please provide +,- value.")
        return value

    @field_validator("delay")
    @classmethod
    def delay_values(cls, value):
        value = value.strip()
        if not value.isnumeric():
            raise ValueError("Please provide numeric value.")
        return value
