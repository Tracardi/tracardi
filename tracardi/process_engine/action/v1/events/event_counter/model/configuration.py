from pydantic import validator
from pytimeparse import parse

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    event_type: NamedEntity
    time_span: str

    @validator("time_span")
    def valid_time_span(cls, value):
        if parse(value.strip("-")) is None:
            raise ValueError("Could not parse {} as time span".format(value))
        return value

