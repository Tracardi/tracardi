from pydantic import BaseModel
from typing import Optional


class CopyIndex(BaseModel):
    from_index: str
    to_index: str
    multi: bool
    script: Optional[str] = None


class MigrationSchema(BaseModel):
    id: str
    copy_index: CopyIndex
    worker: str
    asynchronous: bool
    wait_for_completion: Optional[bool] = True
    params: Optional[dict] = {}
