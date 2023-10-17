from typing import Optional

from pydantic import field_validator
import json
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    index: str
    query: str
    log: Optional[bool] = False

    @field_validator("index")
    @classmethod
    def validate_index(cls, value):
        if len(value) == "":
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("query")
    @classmethod
    def validate_content(cls, value):
        try:
            if isinstance(value, dict):
                value = json.dumps(value)
            return value

        except json.JSONDecodeError as e:
            raise ValueError(str(e))
