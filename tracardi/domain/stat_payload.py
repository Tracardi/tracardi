from datetime import datetime
from typing import List

from pydantic import BaseModel


class StatPayload(BaseModel):
    date: datetime
    event_type: str
    event_tags: List[str] = []
    new_session: bool
