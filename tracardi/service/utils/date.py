from typing import Optional
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta


def now_in_utc(delay=None) -> datetime:

    now = datetime.utcnow().replace(tzinfo=ZoneInfo('UTC'))

    if delay is None:
        return now

    return now + timedelta(seconds=delay)

def is_timezone_aware(dt: datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def add_utc_time_zone_if_none(dt: Optional[datetime]) -> Optional[datetime]:

    if dt is None:
        return None

    if is_timezone_aware(dt):
        return dt

    return dt.replace(tzinfo=ZoneInfo('UTC'))
