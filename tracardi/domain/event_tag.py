from pydantic import BaseModel
from typing import List
from uuid import uuid4


class EventTag(BaseModel):
    type: str = ""
    tags: List[str] = []
