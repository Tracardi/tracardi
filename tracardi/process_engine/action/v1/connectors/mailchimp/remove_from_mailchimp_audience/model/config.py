from pydantic import BaseModel, validator


class Source(BaseModel):
    name: str
    id: str


class Config(BaseModel):
    source: Source
    email: str
    list_id: str
    delete: bool

    @validator("email")
    def validate_email(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("list_id")
    def validate_list_id(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


class Token(BaseModel):
    token: str
