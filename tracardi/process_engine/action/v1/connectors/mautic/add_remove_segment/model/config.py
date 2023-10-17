from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    action: str
    contact_id: str
    segment: str

    @field_validator("action")
    @classmethod
    def validate_action_parameter(cls, value):
        if value is None or value not in ("add", "remove"):
            raise ValueError("Action parameter must be either 'add' or 'remove'.")
        return value

    @field_validator("contact_id")
    @classmethod
    def validate_contact_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
