from typing import Optional, Dict

from tracardi.domain.named_entity import NamedEntity


class Device(NamedEntity):
    type: Optional[str] = None
    properties: Optional[Dict[str, str]] = None