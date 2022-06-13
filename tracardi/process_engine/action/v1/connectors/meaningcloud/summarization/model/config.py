from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Optional


class Config(BaseModel):
    source: NamedEntity
    text: str
    lang: Optional[str] = "auto"
    sentences: str

    @validator("source")
    def must_not_be_empty(cls, value):
        if value.id == "":
            raise ValueError("This field can not be empty")
        return value

    @validator("text")
    def validate_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("sentences")
    def validate_sentences(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        elif not value.isnumeric():
            raise ValueError("This field must contain an integer.")
        return value


class Token(BaseModel):
    token: str

