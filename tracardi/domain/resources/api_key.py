from pydantic import BaseModel, validator


class ApiKey(BaseModel):
    api_key: str

    @validator("api_key")
    def must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Api Key must not be empty.")
        return value
