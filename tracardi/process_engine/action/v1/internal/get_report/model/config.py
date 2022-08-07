from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity
from typing import Union
import json
from tracardi.domain.entity import NullableEntity


class ReportConfig(PluginConfig):
    report: NamedEntity
    params: Union[str, dict]

    @validator("params")
    def handle_empty_params(cls, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("Given report configuration is not a valid JSON.")
        return value

    @validator("report")
    def validate_report(cls, value):
        if not value.id:
            raise ValueError("This field cannot be empty.")
        return value


class Config(PluginConfig):
    report_config: ReportConfig


class ReportEndpointConfig(PluginConfig):
    report: NullableEntity


class EndpointConfig(PluginConfig):
    report_config: ReportEndpointConfig
