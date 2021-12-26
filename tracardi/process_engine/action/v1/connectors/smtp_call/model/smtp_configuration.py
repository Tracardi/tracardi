from pydantic import BaseModel, validator
from typing import Optional
from tracardi.domain.entity import Entity


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
    message: str

    @validator("title")
    def title_must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Title can not be empty.")
        return value

    @validator("message")
    def message_must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Message can not be empty.")
        return value


class Configuration(BaseModel):
    source: Entity
    message: Message
