from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Dict, Any, Optional


class Config(BaseModel):
    source: NamedEntity
    email: str
    additional_mapping: Dict[str, Any]
    overwrite_with_blank: bool

    @validator("email")
    def validate_ip_active_owner(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

