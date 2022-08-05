from pydantic import validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    action: str
    contact_id: str
    points: str

    @validator("action")
    def validate_action(cls, value):
        if value is None or value not in ("add", "subtract"):
            raise ValueError("Action parameter must be either 'add' or 'subtract'.")
        return value

    @validator("contact_id")
    def validate_contact_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("points")
    def validate_points(cls, value):
        if value is None or len(value) == 0 or not value.isnumeric():
            raise ValueError("This field must contain an integer.")
        return value
