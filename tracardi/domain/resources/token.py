from pydantic import BaseModel, validator


class Token(BaseModel):
    token: str

    @validator("token")
    def must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Token must not be empty.")
        return value
