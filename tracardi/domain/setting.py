from datetime import datetime
from typing import Optional, Any

from tracardi.domain.named_entity import NamedEntity


class Setting(NamedEntity):
    timestamp: Optional[datetime] = None
    description: Optional[str] = ""
    enabled: Optional[bool] = False
    type: str
    content: dict
    config: dict

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
