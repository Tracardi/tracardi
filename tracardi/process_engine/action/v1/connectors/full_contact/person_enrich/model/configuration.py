from typing import Optional, List

from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig


class PII(BaseModel):
    email: Optional[str] = None
    emails: Optional[List[str]] = []
    phone: Optional[str] = None
    phones: Optional[List[str]] = []
    location: Optional[str] = None
    name: Optional[str] = None


class Configuration(PluginConfig):
    source: NamedEntity
    pii: PII
    timeout: int = 30
