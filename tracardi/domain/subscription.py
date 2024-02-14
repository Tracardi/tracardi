from typing import Optional, List

from tracardi.domain.named_entity import NamedEntityInContext


class Subscription(NamedEntityInContext):
    description: Optional[str] = ""
    enabled: bool = False
    tags: List[str] = []
    topic: str
    token: str