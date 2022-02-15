from pydantic import BaseModel
from typing import Dict


class Config(BaseModel):
    conditions: Dict[str, str]
