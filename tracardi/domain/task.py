from tracardi.domain.named_entity import NamedEntity
from datetime import datetime
from pydantic import field_validator
from typing import Optional


class Task(NamedEntity):

    """
    This object is for storing background tasks that run for example imports, etc.
    """

    task_id: str
    timestamp: Optional[datetime] = None
    status: str = 'pending'
    progress: float = 0
    type: str
    params: dict = {}

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value not in ("pending", "running", "error", "done", "cancelled"):
            raise ValueError(f"Status must be one of: pending, running, error, done, cancelled. {value} given.")
        return value
