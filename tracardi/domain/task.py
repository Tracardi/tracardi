from tracardi.domain.named_entity import NamedEntity
from datetime import datetime
from pydantic import validator
from typing import Optional


class Task(NamedEntity):
    timestamp: Optional[datetime]
    status: str = 'pending'
    progress: float = 0
    import_type: str = "missing"
    import_id: str
    task_id: str
    event_type: str = "missing"

    @validator("status")
    def validate_status(cls, value):
        if value not in ("pending", "running", "error", "done", "cancelled"):
            raise ValueError(f"Status must be one of: pending, running, error, done, cancelled. {value} given.")
        return value
