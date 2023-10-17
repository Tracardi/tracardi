from pydantic import field_validator, BaseModel
from typing import Optional
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    text: str
    lang: Optional[str] = "auto"
    focus: Optional[str] = None
    company_type: Optional[str] = None
    relaxed_typography: bool

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class Token(BaseModel):
    token: str
