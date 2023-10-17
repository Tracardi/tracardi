from pydantic import field_validator, BaseModel
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class PushOverAuth(BaseModel):
    token: str
    user: str


class PushOverConfiguration(PluginConfig):
    source: NamedEntity
    message: str

    @field_validator("message")
    @classmethod
    def name_not_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Message can not be empty.")
        return value
