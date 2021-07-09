from typing import Optional

from pydantic import BaseModel

from app.domain.pii import PII
from app.service.merger import merge


class Private(BaseModel):
    pii: Optional[PII] = None


class ProfileTraits(BaseModel):
    private: Optional[dict] = {}
    public: Optional[dict] = {}

