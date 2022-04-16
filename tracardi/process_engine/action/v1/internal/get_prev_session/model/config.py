from pydantic import BaseModel, validator


class Config(BaseModel):
    offset: int = -1

    @validator("offset")
    def validate_offset(cls, value):
        if not -10 <= value <= 0:
            raise ValueError("Offset has to be an integer between -10 and 0 inclusively.")
        return value
