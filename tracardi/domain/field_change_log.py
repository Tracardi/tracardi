from datetime import datetime

from typing import List, Any

from tracardi.domain.entity import Entity


class FieldChangeLog(Entity):
    timestamp: datetime
    type: str
    field: str
    value: Any
