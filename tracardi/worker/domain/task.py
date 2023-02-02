from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional


class Task(BaseModel):
    id: str
    name: str
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
