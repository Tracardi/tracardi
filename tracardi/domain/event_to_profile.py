from typing import List
from typing import Optional

from tracardi.domain.named_entity import NamedEntity


class EventToProfile(NamedEntity):
    event_type: str
    description: Optional[str] = "No description provided"
    enabled: Optional[bool] = False
    config: Optional[dict] = {}
    event_to_profile: Optional[dict] = {}
    tags: List[str] = []
