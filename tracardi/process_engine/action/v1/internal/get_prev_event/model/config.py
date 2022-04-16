from pydantic import BaseModel, validator


class Config(BaseModel):
    event_type: str
    offset: int

    @validator("offset")
    def validate_offset(cls, value):
        if not -10 <= value <= 0:
            raise ValueError("Offset must be an integer between -10 and 0 inclusively.")

        return value
