from pydantic import BaseModel
from typing import List


class EventTag(BaseModel):
    type: str = ""
    tags: List[str] = []
