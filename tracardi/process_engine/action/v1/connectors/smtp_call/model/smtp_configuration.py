from pydantic import field_validator, BaseModel
from typing import Optional

from tracardi.domain.content import Content
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class SmtpConfiguration(BaseModel):
    smtp: str
    port: int
    username: str
    password: str
    timeout: int = 15


class Message(BaseModel):
    send_to: str
    send_from: str
    title: str
    reply_to: Optional[str] = None
    message: Content

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Title can not be empty.")
        return value

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, value):
        if len(value.content) < 1:
            raise ValueError("Message can not be empty.")
        return value


class Configuration(PluginConfig):
    resource: NamedEntity
    mail: Message
