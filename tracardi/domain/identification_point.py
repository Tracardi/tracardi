from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity


class IdentificationPoint(Entity):
    name: str
    description: Optional[str] = ""
    source: NamedEntity
    event_type: NamedEntity
    settings: Optional[dict] = {}  # Flattened ES field
