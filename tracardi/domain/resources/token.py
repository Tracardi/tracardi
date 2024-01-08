from pydantic import field_validator, BaseModel


class Token(BaseModel):
    token: str

    @field_validator("token")
    @classmethod
    def must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Token must not be empty.")
        return value
