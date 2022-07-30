from pydantic import validator
from pytimeparse import parse
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity


class Configuration(PluginConfig):
    field: NamedEntity
    time_span: str

    @validator("field")
    def field_not_empty(cls, value):
        if not value or (isinstance(value, NamedEntity) and not value.id):
            raise ValueError("Field name can not be empty")
        return value

    @validator("time_span")
    def valid_time_span(cls, value):
        if parse(value.strip("-")) is None:
            raise ValueError("Could not parse {} as time span".format(value))
        return value
