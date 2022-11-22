from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ProfileConfig(BaseModel):
    traits: dict


class EventConfig(BaseModel):
    profile: Optional[ProfileConfig]
    context: Optional[bool] = True
    request: Optional[bool] = True
    tags: Optional[bool] = True
    aux: Optional[bool] = True


class YamlConfig(BaseModel):
    event: Optional[EventConfig]
