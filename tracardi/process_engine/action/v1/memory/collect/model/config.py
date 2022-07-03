from pydantic import BaseModel, validator


class Config(BaseModel):
    name: str
    type: str = "list"

    @validator("name")
    def must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("This field can not be empty")
        return value.replace(" ", "_")

    @validator("type")
    def must_have_defined_values(cls, value):
        if value.strip() not in ["list", 'dict']:
            raise ValueError("This field accepts only two values: list or dict")
        return value
