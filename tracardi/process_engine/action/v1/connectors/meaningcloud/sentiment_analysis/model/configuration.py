from pydantic import validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    language: str = 'en'
    text: str

    @validator("language")
    def correct_lang(cls, value):
        langs = ["en", "sp", "fr", "it", "pt", "ct"]
        if value not in langs:
            raise ValueError("Incorrect language. Allowed values {}".format(langs))
        return value
