from typing import Optional, List

from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class PII(BaseModel):
    email: Optional[str] = None
    emails: Optional[List[str]] = []
    phone: Optional[str] = None
    phones: Optional[List[str]] = []
    location: Optional[str] = None
    name: Optional[str] = None


class Configuration(BaseModel):
    source: NamedEntity
    pii: PII
    timeout: int = 30
