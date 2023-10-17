from pydantic import field_validator, BaseModel


class Config(BaseModel):
    name: str
    type: str = "list"

    @field_validator("name")
    @classmethod
    def must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("This field can not be empty")
        return value.replace(" ", "_")

    @field_validator("type")
    @classmethod
    def must_have_defined_values(cls, value):
        if value.strip() not in ["list", 'dict']:
            raise ValueError("This field accepts only two values: list or dict")
        return value
