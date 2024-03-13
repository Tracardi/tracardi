from json import JSONDecodeError

import json
from typing import Optional
from tracardi.service.plugin.domain.config import PluginConfig
from pydantic import field_validator


class Config(PluginConfig):
    content: Optional[str] = ""
    attributes: Optional[str] = "{}"

    @field_validator("attributes")
    @classmethod
    def validate_file_path(cls, value):
        try:
            json.loads(value)
            return value
        except JSONDecodeError:
            raise ValueError("Could not parse invalid JSON object.")
