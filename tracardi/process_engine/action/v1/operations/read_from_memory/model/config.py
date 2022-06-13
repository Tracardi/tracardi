from pydantic import BaseModel, validator


class Config(BaseModel):
    key: str

    @validator("key")
    def must_not_be_empty(cls, value):
        if value == "":
            raise ValueError("This field can not be empty")
        return value
