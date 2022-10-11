from pydantic import validator

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    source: NamedEntity
    tweet: str

    @validator('tweet')
    def check_given_tweet(cls, value):
        if not value:
            raise ValueError("Please fill tweet field with content which you want to send.")
        return value
