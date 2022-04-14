from pydantic import BaseModel, validator


class Config(BaseModel):
    offset: int

    @validator("offset")
    def validate_offset(cls, value):
        if not -10 <= value < 0:
            raise ValueError("Offset has to be a negative integer between -10 and -1 inclusively.")
        return value
