from typing import Optional

from pydantic import BaseModel

from tracardi.domain.entity import Entity


class CustomerConsent(BaseModel):
    source: Entity
    session: Entity
    profile: Entity
    consents: Optional[dict] = {}
