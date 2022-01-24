from pydantic import BaseModel, validator
from typing import List, Optional
from pytimeparse import parse


class ConsentType(BaseModel):
    name: str
    description: str
    revokable: bool
    default_value: str
    enabled: bool = True
    tags: List[str] = []
    required: bool = False
    auto_revoke: Optional[str] = None

    @validator("default_value")
    def default_value_validator(cls, value):
        if value not in ("grant", "deny"):
            raise ValueError("'default_value' must be either 'grant' or 'deny'")
        return value

    @validator('auto_revoke')
    def auto_revoke_validator(cls, value):
        if (value is not None and value != "") and (parse(value) is None or parse(value) < 0):
            raise ValueError("Auto-revoke time is in invalid form. If you do not want to auto "
                             "revoke consent leave it empty.")
        return value
