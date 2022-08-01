from typing import Optional

from pydantic import BaseModel, validator
import json

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig
from typing import Union, List


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


class ElasticCredentials(BaseModel):
    url: Union[str, List[str]]
    port: int
    scheme: str
    username: Optional[str] = None
    password: Optional[str] = None
    verify_certs: bool

    def has_credentials(self):
        return self.username is not None and self.password is not None

    def get_url(self):
        return [self.url] if isinstance(self.url, str) else self.url
