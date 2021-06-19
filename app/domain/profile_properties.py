from typing import Optional

from pydantic import BaseModel

from app.domain.pii import PII


class Private(BaseModel):
    pii: Optional[PII] = None


class ProfileProperties(BaseModel):
    private: Optional[dict] = {}
    public: Optional[dict] = {}
