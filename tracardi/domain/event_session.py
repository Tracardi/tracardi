from typing import Optional

from datetime import datetime

from tracardi.domain.entity import Entity
from tracardi.service.utils.date import now_in_utc


class EventSession(Entity):
    start: datetime = now_in_utc()
    duration: float = 0
    tz: Optional[str] = None