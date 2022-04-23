from pydantic import BaseModel
from typing import List, Dict


class Config(BaseModel):
    consent_ids: List[Dict]
    require_all: bool


