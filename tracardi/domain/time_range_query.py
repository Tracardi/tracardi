import pytz
from _datetime import datetime, timedelta
from typing import Optional, Tuple
from pydantic import BaseModel
from enum import Enum


class DatetimeType(str, Enum):
    second = 'second'
    minute = 'minute'
    hour = 'hour'
    day = 'day'
    week = 'week'
    month = 'month'
    year = 'year'


class DateDeltaPayload(BaseModel):
    value: int
    entity: DatetimeType

    def get_delta(self):
        entity = self.entity
        value = abs(self.value)

        if entity in ['second', 'seconds']:
            return timedelta(seconds=value)
        elif entity in ['minute', 'minutes']:
            return timedelta(minutes=value)
        elif entity in ['hour', 'hours']:
            return timedelta(hours=value)
        elif entity in ['day', 'days']:
            return timedelta(days=value)
        elif entity in ['week', 'weeks']:
            return timedelta(weeks=value)
        elif entity in ['month', 'months']:
            return timedelta(days=value * 31)
        elif entity in ['year', 'years']:
            return timedelta(days=value * 356)

        return None


class DatetimePayload(BaseModel):
    second: int = None
    minute: int = None
    hour: int = None
    date: int = None
    month: int = None
    year: int = None
    meridiem: str = None
    timeZone: int = 0

    @staticmethod
    def now():
        now = datetime.utcnow()
        return DatetimePayload(year=now.year, month=now.month, date=now.day,
                               hour=now.hour, minute=now.minute, second=now.second,
                               meridiem=now.strftime("%p"))

    def is_set(self):
        return self.year is not None \
               and self.month is not None \
               and self.date is not None \
               and self.hour is not None \
               and self.minute is not None \
               and self.second is not None \
               and self.meridiem is not None

    def get_date(self) -> [datetime, None]:
        if self.is_set():
            return datetime(year=self.year,
                            month=self.month,
                            day=self.date,
                            hour=self.hour,
                            minute=self.minute,
                            second=self.second)
        return None

    def __str__(self):
        return "{}/{}/{} {}:{}:{} {}{}{:02d}".format(
            self.year,
            self.month,
            self.date,
            self.hour,
            self.minute,
            self.second,
            self.meridiem,
            "+" if self.timeZone >= 0 else "-",
            self.timeZone
        )


class DatePayload(BaseModel):
    delta: Optional[DateDeltaPayload] = None
    absolute: Optional[DatetimePayload] = None

    def get_date(self) -> datetime:
        if self.absolute is None:
            absolute_date = datetime.now()
        else:
            absolute_date = self.absolute.get_date()

            # If absolute date is None, Then use now

            if absolute_date is None:
                absolute_date = datetime.now()

        # Get delta
        if self._is_delta_set():
            delta, sign = self._get_delta()
            return absolute_date + (sign * delta)

        return absolute_date

    def is_absolute(self):
        return self.absolute is not None and not self._is_delta_set()

    def _is_delta_set(self) -> bool:
        return self.delta is not None

    def _get_delta(self) -> (delta, int):
        return self.delta.get_delta(), -1 if self.delta.value < 0 else 1


class DatetimeRangePayload(BaseModel):
    minDate: Optional[DatePayload] = None
    maxDate: Optional[DatePayload] = None
    where: Optional[str] = ""
    timeZone: Optional[str] = None
    offset: int = 0
    limit: int = 20
    rand: Optional[float] = 0

    def get_dates(self) -> (datetime, datetime):

        if self._is_now(self.minDate):
            self.minDate = DatePayload(absolute=DatetimePayload.now())

        if self._is_now(self.maxDate):
            self.maxDate = DatePayload(absolute=DatetimePayload.now())

        print("_is_min_date_absolute", self._is_min_date_absolute())
        print("_is_max_date_absolute", self._is_max_date_absolute())

        # Set Anchor date
        if self._is_min_date_absolute() and not self._is_max_date_absolute():
            self.maxDate.absolute = self.minDate.absolute
        elif not self._is_min_date_absolute() and self._is_max_date_absolute():
            self.minDate.absolute = self.maxDate.absolute
        elif not self._is_min_date_absolute() and not self._is_max_date_absolute():
            self.minDate.absolute = DatetimePayload.now()
            self.maxDate.absolute = DatetimePayload.now()

        min_date = self.minDate.get_date()
        max_date = self.maxDate.get_date()

        if min_date > max_date or min_date == max_date:
            raise ValueError(
                "Incorrect time range. From date `{}` is earlier then to date `{}` or dates are equal.".format(
                    min_date, max_date
                ))

        return min_date, max_date

    def _is_now(self, date: DatePayload):
        return date is None or (date.absolute is None and date.delta is None)

    def _is_min_date_absolute(self):
        return self.minDate is None or self.minDate.is_absolute()

    def _is_max_date_absolute(self):
        return self.maxDate is None or self.maxDate.is_absolute()

    @staticmethod
    def convert_to_local_datetime(utc_datetime, timezone) -> Tuple[datetime, Optional[str]]:
        try:
            local_tz = pytz.timezone(timezone)
            local_dt = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            return local_tz.normalize(local_dt), timezone  # .normalize might be unnecessary
        except pytz.exceptions.UnknownTimeZoneError as e:
            # todo log error
            return utc_datetime, None
