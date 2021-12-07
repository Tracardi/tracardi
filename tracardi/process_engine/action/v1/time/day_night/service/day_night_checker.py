from datetime import datetime
from typing import Tuple
from astral import LocationInfo
from astral.sun import sun
import pytz


def day_night_split(time_now: datetime, latitude: str, longitude: str) -> Tuple[datetime, datetime]:

    loc_info = LocationInfo(latitude=float(latitude), longitude=float(longitude))
    sun_info = sun(loc_info.observer, date=time_now)

    return sun_info['sunrise'], sun_info['sunset']


def is_day(latitude: str, longitude: str):
    now = datetime.now()

    utc = pytz.UTC
    now = now.replace(tzinfo=utc)

    sun_rise, sun_set = day_night_split(now, latitude, longitude)

    return sun_rise < now < sun_set
