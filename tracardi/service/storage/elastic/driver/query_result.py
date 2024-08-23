from typing import List, Any

from pydantic import BaseModel


class QueryResult(BaseModel):
    total: int
    result: List[Any]
