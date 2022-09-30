from typing import Optional
from pydantic import BaseModel, validator


class Configuration(BaseModel):
    id: str
    type: str
    reference_profile: bool = True
    properties: Optional[str] = "{}"
    traits: Optional[str] = "{}"

    @validator("id")
    def id_must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("This field can not be empty")
        return value.strip()

    @validator("type")
    def type_must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("This field can not be empty")
        return value.strip()


