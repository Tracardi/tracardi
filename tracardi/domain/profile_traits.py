from typing import Optional

from pydantic import BaseModel

from tracardi.domain.pii import PII
from tracardi.service.merger import merge


class Private(BaseModel):
    pii: Optional[PII] = None


class ProfileTraits(BaseModel):
    private: Optional[dict] = {}
    public: Optional[dict] = {}

