from typing import List, Optional, Union

from pydantic import validator

from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    interest: Union[str, List[str]]
    value: Optional[str] = "1.0"

    @validator("interest")
    def is_not_empty(cls, value):
        if not value:
            raise ValueError("Interest cannot be empty. ")
        return value

    @validator("value")
    def is_numeric(cls, value):
        if not value.replace('.', '', 1).isnumeric():
            raise ValueError("Interest value must a number. ")
        return value
