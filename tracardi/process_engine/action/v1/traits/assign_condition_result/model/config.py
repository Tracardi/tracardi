from pydantic import BaseModel, validator
from typing import Dict


class Config(BaseModel):
    conditions: Dict[str, str]

    @validator("conditions")
    def validate_conditions(cls, value):
        for key in value:
            if not key.startswith("profile@"):
                raise ValueError("Given keys should be paths starting with 'profile@'")
        return value
