from pydantic import BaseModel
from typing import Optional


class MigrationSchema(BaseModel):
    id: str
    index: str
    multi: bool
    script: Optional[str] = None
    worker: str
    asynchronous: bool
    from_index: Optional[str] = None
    to_index: Optional[str] = None
