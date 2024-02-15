from uuid import uuid4

from typing import Any

from datetime import datetime

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.utils.date import now_in_utc


class Configuration(NamedEntity):
    timestamp: datetime
    properties: dict

    def __init__(self, **data: Any):
        if 'id' not in data:
            data['id'] = str(uuid4())
        if 'timestamp' not in data:
            data['timestamp'] = now_in_utc()

        super().__init__(**data)
