from pydantic import validator, BaseModel
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity
from typing import Union
import json


class ReportConfig(BaseModel):
    report: NamedEntity
    params: Union[str, dict]


class Config(PluginConfig):
    report_config: ReportConfig

    @validator("report_config")
    def validate_report(cls, value):
        if not value.report.id:
            raise ValueError("Report has to be selected.")
        if isinstance(value.params, str):
            try:
                value.params = json.loads(value.params)
            except json.JSONDecodeError:
                raise ValueError("Given report configuration is not a valid JSON.")
        return value
