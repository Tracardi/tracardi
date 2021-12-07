from typing import Union

import pytz
from datetime import datetime
from pydantic import BaseModel, validator


class TimeSpanConfiguration(BaseModel):
    timezone: str
    start: Union[str, datetime]
    end: Union[str, datetime]

    @validator("start")
    def validate_start_time(cls, value):
        try:
            return datetime.strptime(value, '%H:%M:%S')
        except ValueError as e:
            raise e

    @validator("end")
    def validate_end_time(cls, value):
        try:
            return datetime.strptime(value, '%H:%M:%S')
        except ValueError as e:
            raise e

    @staticmethod
    def _convert(hour_string):
        return datetime.strptime(hour_string, '%H:%M:%S')

    def is_in_timespan(self):
        now = datetime.utcnow()

        tz = pytz.timezone(self.timezone)
        local_now = now.replace(tzinfo=pytz.utc).astimezone(tz)

        hour_string = datetime.strftime(local_now, '%H:%M:%S')
        now_hour = self._convert(hour_string)

        return self.start < now_hour < self.end
