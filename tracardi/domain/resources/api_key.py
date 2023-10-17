from pydantic import field_validator, BaseModel


class ApiKey(BaseModel):
    api_key: str

    @field_validator("api_key")
    @classmethod
    def must_not_be_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Api Key must not be empty.")
        return value
