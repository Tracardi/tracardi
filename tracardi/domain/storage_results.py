from typing import Any, List

from pydantic import BaseModel


class StorageResults(BaseModel):
    total: int
    result: List[Any]