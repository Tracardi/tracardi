from typing import Optional

from pydantic import field_validator
import json
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig

class Config(PluginConfig):
    index: str
    documents: str
    source: NamedEntity
    identifier: str
    log: Optional[bool] = False

    @field_validator("index")
    @classmethod
    def validate_index(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
    
    @field_validator("documents")
    @classmethod
    def validate_documents(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
