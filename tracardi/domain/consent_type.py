from pydantic import BaseModel, validator


class ConsentType(BaseModel):
    name: str
    description: str
    revokable: bool
    default_value: str

    @validator("default_value")
    def default_value_validator(cls, v):
        if v not in ("grant", "deny"):
            raise ValueError("'default_value' must be either 'grant' or 'deny'")
        return v
