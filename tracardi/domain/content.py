from pydantic import field_validator, BaseModel


class Content(BaseModel):
    content: str
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if value not in ("text/plain", "text/html"):
            raise ValueError("Message content type must be either text/html or plain text/plain.")
        return value
