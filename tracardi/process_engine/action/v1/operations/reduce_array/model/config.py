from pydantic import BaseModel, validator


class Config(BaseModel):
    array: str

    @validator("array")
    def validate_array(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value
