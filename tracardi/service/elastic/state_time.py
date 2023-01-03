import asyncio
from collections import namedtuple, defaultdict
from datetime import timedelta
from pprint import pprint
from typing import List, Optional
from dateutil import parser
from tracardi.service.storage.driver import storage


async def get_event_field_value_duration_time(event_type: str, fields: List[str], source_id: str = None):
    search_by = [('type', event_type)]
    if source_id:
        search_by.append(
            ('source.id', source_id)
        )
    chunk_result = storage.driver.event.get_all_events_by_fields(search_by, fields + ["metadata.time.insert"])
    point_in_times = {}
    PointInTime = namedtuple("PointInTime", "start_time end_time")
    i = 0
    times_per_period = defaultdict(list)
    last_key = None
    async for result in chunk_result:
        for event in result:
            i += 1
            props = event['properties']
            for field in props:
                now = parser.parse(event['metadata']['time']['insert'])
                value = props[field]
                if i >= 10 and i < 13:
                    value = 2
                if i >= 20 and i < 33:
                    value = 3

                key = f"{field}={value}"

                if key not in point_in_times:
                    point_in_times[key] = PointInTime(now, now)

                if last_key is None or key == last_key:
                    # Still the same value
                    point_in_times[key] = PointInTime(point_in_times[key].start_time, now)
                else:
                    # Key has changed
                    point_in_times[last_key] = PointInTime(point_in_times[last_key].start_time, now)
                    # Append and delete old value
                    times_per_period[last_key].append(point_in_times[last_key])
                    del point_in_times[last_key]

                last_key = key
    # finish
    times_per_period[last_key].append(point_in_times[last_key])

    durations_per_period = {key: [(value.end_time - value.start_time) for value in values] for key, values in times_per_period.items()}
    total_durations_per_period = {key: timedelta(seconds=sum([(value.end_time - value.start_time).total_seconds() for value in values])) for key, values in
           times_per_period.items()}

    result = {key: {
        "periods": values,
        "total": total_durations_per_period[key]
    } for key, values in durations_per_period.items()}
    pprint(result)


asyncio.run(get_event_field_value_duration_time("profile-interest", ['properties.Vacation']))
