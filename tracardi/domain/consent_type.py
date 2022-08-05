from pydantic import BaseModel, validator
from typing import List, Optional
from pytimeparse import parse


class ConsentType(BaseModel):
    name: str
    description: str
    revokable: bool = False
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
    def auto_revoke_validator(cls, value, values):
        if (value is not None and value != "") and (parse(value) is None or parse(value) < 0):
            raise ValueError("Auto-revoke time is in invalid form.")
        if 'revokable' in values and values['revokable'] is True and not value:
            raise ValueError("Auto-revoke time can not be empty if you require the consent to be revoked.")
        return value
