from typing import Optional

from pydantic import BaseModel


class Configuration(BaseModel):
    id: str
    type: str
    reference_profile: bool = True
    properties: Optional[str] = "{}"
    traits: Optional[str] = "{}"
