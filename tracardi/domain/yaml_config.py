from typing import Optional

from pydantic import BaseModel


class ProfileConfig(BaseModel):
    traits: dict


class EventConfig(BaseModel):
    profile: Optional[ProfileConfig] = None
    context: Optional[bool] = True
    request: Optional[bool] = True
    tags: Optional[bool] = True
    aux: Optional[bool] = True


class YamlConfig(BaseModel):
    event: Optional[EventConfig] = None
