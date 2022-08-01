from pydantic import validator
import json
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    index: NamedEntity
    query: str

    @validator("index")
    def validate_index(cls, value):
        if value is None or (isinstance(value, NamedEntity) and not value.id):
            raise ValueError("This field cannot be empty.")
        return value

    @validator("query")
    def validate_content(cls, value):
        try:
            if isinstance(value, dict):
                value = json.dumps(value)
            return value

        except json.JSONDecodeError as e:
            raise ValueError(str(e))
