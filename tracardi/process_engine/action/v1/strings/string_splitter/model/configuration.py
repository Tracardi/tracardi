from pydantic import validator
from pydantic.main import BaseModel


class Configuration(BaseModel):
    string: str
    delimiter: str

    @validator('string')
    def myst_have_2_letter(cls, v):
        if len(v) < 2:
            raise ValueError('String is too short. String must be at least two letters long.')
        return v

