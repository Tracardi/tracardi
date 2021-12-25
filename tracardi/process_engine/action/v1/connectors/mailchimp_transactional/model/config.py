from pydantic import BaseModel, validator


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


class SourceInfo(BaseModel):
    name: str
    id: str


class Config(BaseModel):
    source: SourceInfo
    sender_email: str = None
    message: Message


class Token(BaseModel):
    token: str
