from pydantic import BaseModel
from typing import Optional, List


class MigrationPayload(BaseModel):
    from_version: str
    to_version: str
    from_prefix: Optional[str] = None
    to_prefix: Optional[str] = None
    ids: List[str]
