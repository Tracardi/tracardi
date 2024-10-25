from typing import Optional, Dict
from tracardi.worker.domain.named_entity import NamedEntity


class Application(NamedEntity):
    type: Optional[str] = None  # Browser, App1
    version: Optional[str] = None
    properties: Optional[Dict[str, str]] = None
