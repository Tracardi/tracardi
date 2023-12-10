from zoneinfo import ZoneInfo
from datetime import datetime


def now_in_utc():
    return datetime.utcnow().replace(tzinfo=ZoneInfo('UTC'))