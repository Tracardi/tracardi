from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    language: str = 'en'
    text: str

    @validator("language")
    def correct_lang(cls, value):
        langs = ["en", "sp", "fr", "it", "pt", "ct"]
        if value not in langs:
            raise ValueError("Incorrect language. Allowed values {}".format(langs))
        return value
