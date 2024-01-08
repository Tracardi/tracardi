from pydantic import field_validator, BaseModel


class Config(BaseModel):
    reshape: str = ""
    default: bool = True
    type: str = 'dict'

    @field_validator("type")
    @classmethod
    def must_have_defined_values(cls, value):
        if value.strip() not in ["list", 'dict']:
            raise ValueError("This field accepts only two values: list or dict")
        return value
