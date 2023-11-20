from pydantic import BaseModel
from typing import List, Optional


class EventTag(BaseModel):
    type: Optional[str] = ""
    tags: List[str] = []
