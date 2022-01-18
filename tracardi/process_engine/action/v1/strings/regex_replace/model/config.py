from pydantic import BaseModel, validator


class Config(BaseModel):
    string: str
    find_regex: str
    replace_with: str

    @validator("string")
    def validate_string_value(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("find_regex")
    def validate_find_regex(cls, value):
        if len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

