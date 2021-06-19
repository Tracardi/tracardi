from datetime import datetime
from typing import Optional
from app.domain.entity import Entity


class UserConsent(Entity):
    granted: bool
    revoke: Optional[datetime] = None
