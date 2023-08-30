from pydantic import field_validator, BaseModel
from tracardi.domain.named_entity import NamedEntity
from typing import Optional
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    source: NamedEntity
    text: str
    lang: Optional[str] = "auto"
    sentences: str

    @field_validator("source")
    @classmethod
    def must_not_be_empty(cls, value):
        if value.id == "":
            raise ValueError("This field can not be empty")
        return value

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("sentences")
    @classmethod
    def validate_sentences(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        elif not value.isnumeric():
            raise ValueError("This field must contain an integer.")
        return value


class Token(BaseModel):
    token: str

