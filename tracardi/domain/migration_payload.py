from pydantic import BaseModel
from typing import Optional, List


class MigrationPayload(BaseModel):
    from_version: str
    from_tenant_name: Optional[str] = None
    ids: List[str]
