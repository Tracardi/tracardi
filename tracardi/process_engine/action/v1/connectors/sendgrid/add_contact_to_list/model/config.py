from typing import Dict, Any

from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Content(BaseModel):
    content: str
    type: str

    @validator("type")
    def validate_type(cls, value):
        if value not in ("text/plain", "text/html"):
            raise ValueError("Message content type must be either HTML or plain text.")
        return value


class Message(BaseModel):
    recipient: str
    subject: str = ""
    content: Content

    @validator("recipient")
    def recipient_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Recipient e-mail can not be empty.")
        return value

    @validator("subject")
    def validate_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Subject must be at least one character long.")
        return value


class Config(PluginConfig):
    source: NamedEntity
    email: str
    list_ids: str
    additional_mapping: Dict[str, Any]

    @validator("email")
    def sender_email_subject(cls, value):
        if len(value) == 0:
            raise ValueError("E-mail can not be empty.")
        return value


class Token(BaseModel):
    token: str
