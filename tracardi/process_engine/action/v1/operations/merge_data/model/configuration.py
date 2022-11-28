from enum import Enum
from typing import Optional

from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig


class Connection(str, Enum):
    override = "override"
    merge = "merge"


class Configuration(PluginConfig):
    source: Optional[str] = "{}"
    data: Optional[str] = "{}"
    connection: Connection

    class ConnectionConfig:
        use_enum_values = True


    @validator('source', 'data')
    def validate_if_fields_are_not_empty(cls, value):
        if not value:
            raise ValueError("Source and data fields cannot be empty")
        return value