from pydantic import BaseModel, validator


class Content(BaseModel):
    content: str
    type: str

    @validator("type")
    def validate_type(cls, value):
        if value not in ("text/plain", "text/html"):
            raise ValueError("Message content type must be either text/html or plain text/plain.")
        return value
