from tracardi.domain.named_entity import NamedEntity
from datetime import datetime
from pydantic import validator
from typing import Optional


class Task(NamedEntity):

    """
    This object is for storing background tasks that run for example imports, etc.
    """

    task_id: str
    timestamp: Optional[datetime]
    status: str = 'pending'
    progress: float = 0
    type: str
    params: dict = {}

    @validator("status")
    def validate_status(cls, value):
        if value not in ("pending", "running", "error", "done", "cancelled"):
            raise ValueError(f"Status must be one of: pending, running, error, done, cancelled. {value} given.")
        return value
