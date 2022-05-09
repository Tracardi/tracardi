from tracardi.domain.named_entity import NamedEntity
from datetime import datetime
from pydantic import validator
from typing import Optional


class Task(NamedEntity):
    timestamp: Optional[datetime] = datetime.utcnow()
    status: str
    progress: float
    import_id: str

    @validator("status")
    def validate_status(cls, value):
        if value not in ("pending", "running", "error", "done", "cancelled"):
            raise ValueError(f"Status must be one of: pending, running, error, done, cancelled. {value} given.")
        return value
