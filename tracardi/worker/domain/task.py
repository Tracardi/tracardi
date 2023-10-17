from pydantic import field_validator, BaseModel
from datetime import datetime
from typing import Optional


class Task(BaseModel):
    id: str
    name: str
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
