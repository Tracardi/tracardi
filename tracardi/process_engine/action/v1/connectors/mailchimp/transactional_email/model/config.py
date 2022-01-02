from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity


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


class Config(BaseModel):
    source: NamedEntity
    sender_email: str
    message: Message

    @validator("sender_email")
    def sender_email_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Sender e-mail can not be empty.")
        return value


class Token(BaseModel):
    token: str
