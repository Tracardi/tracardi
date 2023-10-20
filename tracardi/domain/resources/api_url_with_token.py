from typing import Optional

from pydantic import field_validator, BaseModel


class ApiUrlToken(BaseModel):
    host: Optional[str] = 'https://api.novu.co'
    token: str

    @field_validator("token")
    @classmethod
    def token_must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Token must not be empty.")
        return value

    @field_validator("host")
    @classmethod
    def host_must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Host must not be empty.")
        return value
