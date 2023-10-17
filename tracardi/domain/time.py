from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class Time(BaseModel):
    insert: Optional[datetime] = None
    create: Optional[datetime] = None
    update: Optional[datetime] = None

    def __init__(self, **data: Any):
        if 'insert' not in data:
            data['insert'] = datetime.utcnow()
        super().__init__(**data)


class ProfileVisit(BaseModel):
    last: Optional[datetime] = None
    current: Optional[datetime] = None
    count: int = 0
    tz: Optional[str] = None

    def had_previous_visit(self):
        return self.current is not None

    def set_visits_times(self):
        if self.had_previous_visit():
            self.last = self.current
        self.current = datetime.utcnow()


class ProfileTime(Time):
    segmentation: Optional[datetime] = None
    # Inherits from Time
    visit: ProfileVisit = ProfileVisit()


class EventTime(Time):
    process_time: Optional[float] = 0
    total_time: Optional[float] = 0

