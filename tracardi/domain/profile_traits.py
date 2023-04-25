from typing import Optional
from pydantic import BaseModel
from tracardi.domain.pii import PII


class Private(BaseModel):
    pii: Optional[PII] = None


