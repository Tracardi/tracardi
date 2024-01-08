from tracardi.service.utils.date import now_in_utc

from datetime import datetime

import tzlocal

from tracardi.event_server.utils.timezone import get_timezone

dt = datetime.now()
print(dt.astimezone())
print(tzlocal.get_localzone().utcoffset(dt))
print()
dt = now_in_utc()
print(dt)
print(dt.astimezone())
print()
import pytz
my_date = datetime.now(pytz.timezone('Europe/Warsaw'))
print(my_date)
print(get_timezone())