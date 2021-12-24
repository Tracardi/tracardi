from pydantic import BaseModel, validator
from tracardi.service.mailchimp_sender import MailChimpTransactionalSender


class Content(BaseModel):
    content: str = None
    type: str = None

    @validator("type")
    def validate_type(cls, value):
        if value not in ("text/plain", "text/html"):
            raise ValueError("Message content type must be either HTML or plain text.")
        return value


class Message(BaseModel):
    recipient: str = None
    subject: str = ""
    content: Content

    @validator("subject")
    def validate_subject(cls, value):
        if len(value) == 0:
            raise ValueError("Subject must be at least one character long.")
        return value


class Config(BaseModel):
    api_key: str = None
    sender_email: str = None
    message: Message

    @validator("api_key")
    def validate_api_key(cls, value):
        MailChimpTransactionalSender.validate_api_key(value)
        return value
