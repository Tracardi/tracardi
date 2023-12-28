from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

from tracardi.service.utils.date import now_in_utc, add_utc_time_zone_if_none


class Time(BaseModel):
    insert: Optional[datetime] = None
    create: Optional[datetime] = None
    update: Optional[datetime] = None

    def __init__(self, **data: Any):
        if 'insert' not in data:
            data['insert'] = now_in_utc()
        super().__init__(**data)

        self.insert = add_utc_time_zone_if_none(self.insert)
        self.create = add_utc_time_zone_if_none(self.create)
        self.update = add_utc_time_zone_if_none(self.update)



class ProfileVisit(BaseModel):
    last: Optional[datetime] = None
    current: Optional[datetime] = None
    count: int = 0
    tz: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.last = add_utc_time_zone_if_none(self.last)
        self.current = add_utc_time_zone_if_none(self.current)

    def had_previous_visit(self):
        return self.current is not None

    def set_visits_times(self):
        if self.had_previous_visit():
            self.last = self.current
        self.current = now_in_utc()


class ProfileTime(Time):
    segmentation: Optional[datetime] = None
    # Inherits from Time
    visit: ProfileVisit = ProfileVisit()


class EventTime(Time):
    process_time: Optional[float] = 0
    total_time: Optional[float] = 0

