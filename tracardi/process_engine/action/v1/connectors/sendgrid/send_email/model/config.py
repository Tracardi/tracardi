from pydantic import field_validator, BaseModel
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class Content(BaseModel):
    content: str
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if value not in ("text/plain", "text/html"):
            raise ValueError("Message content type must be either HTML or plain text.")
        return value


class Message(BaseModel):
    recipient: str
    subject: str = ""
    content: Content

    @field_validator("recipient")
    @classmethod
    def recipient_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Recipient e-mail can not be empty.")
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Subject must be at least one character long.")
        return value


class Config(PluginConfig):
    source: NamedEntity
    sender_email: str
    message: Message

    @field_validator("sender_email")
    @classmethod
    def sender_email_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Sender e-mail can not be empty.")
        return value


class Token(BaseModel):
    token: str
