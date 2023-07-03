from typing import Optional, List

from pydantic import BaseModel


class QueryResult(BaseModel):
    total: int
    result: list
    buckets: Optional[List[str]] = []
