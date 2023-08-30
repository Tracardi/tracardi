from typing import List, Optional, Union

from pydantic import field_validator

from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    interest: Union[str, List[str]]
    value: Optional[str] = "1.0"

    @field_validator("interest")
    @classmethod
    def is_not_empty(cls, value):
        if not value:
            raise ValueError("Interest cannot be empty. ")
        return value

    @field_validator("value")
    @classmethod
    def is_numeric(cls, value):
        if not value.replace('.', '', 1).isnumeric():
            raise ValueError("Interest value must a number. ")
        return value
