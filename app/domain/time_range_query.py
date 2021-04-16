from _datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TimeRangeQuery(BaseModel):
    min: datetime
    max: datetime
    query: Optional[str] = ""
    offset: int = 0
    limit: int = 20
    rand: Optional[float] = 0



