from pydantic import field_validator, BaseModel
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.named_entity import NamedEntity


class Config(PluginConfig):
    source: NamedEntity
    email: str
    list_id: NamedEntity
    delete: bool

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("list_id")
    @classmethod
    def validate_list_id(cls, value):
        if value is None or len(value.id) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class Token(BaseModel):
    token: str
