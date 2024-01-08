from pydantic import field_validator, BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Optional
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    project_id: str
    funnel_id: str
    from_date: str
    to_date: Optional[str] = None

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, value):
        if len(value) == 0 or not value.isnumeric():
            raise ValueError("Project ID must be a number.")
        return int(value)

    @field_validator('funnel_id')
    @classmethod
    def validate_funnel_id(cls, value):
        if len(value) == 0 or not value.isnumeric():
            raise ValueError("Funnel ID must be a number.")
        return int(value)

    @field_validator("from_date")
    @classmethod
    def validate_from_date(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty")
        return value


class MixPanelCredentials(BaseModel):
    username: str
    password: str
    server_prefix: str

    @field_validator("server_prefix")
    @classmethod
    def validate_server_prefix(cls, value):
        if value.lower() not in ("us", "eu"):
            raise ValueError("Server prefix value must be either US or EU.")
        return value
