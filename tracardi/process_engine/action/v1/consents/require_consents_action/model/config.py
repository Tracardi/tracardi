from pydantic import BaseModel
from typing import List


class Config(BaseModel):
    consent_ids: List[str]
    require_all: bool
