import asyncio
from collections import namedtuple, defaultdict
from datetime import timedelta, datetime
from pprint import pprint
from typing import List, Optional, Tuple
from dateutil import parser
from dotty_dict import dotty

from tracardi.service.storage.driver import storage

PointInTime = namedtuple("PointInTime", "start_time end_time")
FieldAndValue = namedtuple("EventAndValue", "field value")


class EventsInTime:

    def __init__(self):
        self.events = defaultdict(dict)
        self.last_values = {}
        self.start_time = None

    def init(self, key: FieldAndValue, now):
        if not self.contains(key, with_value=False):
            # Created previously bu value detected
            self.events[key.field][key.value] = PointInTime(now, now)
        elif not self.contains(key, with_value=True):  # does contain field without value
            # Never created
            self.events[key.field][key.value] = PointInTime(self.start_time, now)

    def set(self, key: FieldAndValue, now, update="end") -> bool:
        if update == "end":
            self.events[key.field][key.value] = PointInTime(self[key].start_time, now)
        else:
            self.events[key.field][key.value] = PointInTime(now, now)

        is_changed = self.has_changed(key)
        self.last_values[key.field] = key.value
        return is_changed

    def commit(self, key: FieldAndValue):
        self.last_values[key.field] = key.value  # eg. last_values['type'] = 'page_view'

    def __getitem__(self, key: FieldAndValue) -> PointInTime:
        return self.events[key.field][key.value]

    def __delitem__(self, key: FieldAndValue):
        del self.events[key.field][key.value]

    def contains(self, key: FieldAndValue, with_value = True) -> bool:
        if with_value:
            return key.field in self.events and key.value in self.events[key.field]
        return key.field in self.events

    def has_changed(self, key: FieldAndValue) -> bool:
        if key.field not in self.last_values:
            return False
        return key.value != self.last_values[key.field]

    def set_start(self, now):
        self.start_time = now


async def get_event_field_value_duration_time(event_type: str, fields: List[str], source_id: str = None,
                                              range: Optional[Tuple[datetime, datetime]] = None):
    search_by = [('type', event_type)]
    if source_id:
        search_by.append(
            ('source.id', source_id)
        )

    chunk_result = storage.driver.event.get_all_events_by_fields(search_by, fields + ["metadata.time.insert"])
    point_in_times = EventsInTime()

    record_no = 0
    chunk_no = 0
    key = False
    last_key_per_field = {}
    times_per_period = defaultdict(list)
    async for result in chunk_result:
        chunk_no += 1

        for event in result:

            flat_event = dotty(event)
            record_no += 1
            for field in fields:

                now = parser.parse(event['metadata']['time']['insert'])

                if record_no == 1 and chunk_no == 1:
                    point_in_times.set_start(now)

                try:
                    value = flat_event[field]
                except KeyError:
                    continue

                if (record_no == 2 or record_no == 3 or record_no == 4 or record_no == 6) and field == 'type':
                    value = 2
                if (record_no == 3) and field == 'properties.Vacation':
                    value = 3

                key = FieldAndValue(field, value)

                # Sets point in time if not available
                point_in_times.init(key, now)

                is_changed = point_in_times.has_changed(key)

                point_in_times.set(key, now, update="end")

                if is_changed:
                    last_key = last_key_per_field[key.field] if key.field in last_key_per_field else key
                    times_per_period[last_key].append(point_in_times[key])
                    print("Changed", f"{key.field}={last_key.value}->{key.value}",  point_in_times[key])
                    # This value will start again
                    point_in_times.set(key, now, update="start")

                print(f"{record_no}    {is_changed}    {key.field}  {point_in_times[key].start_time}   {now}   {key.field}={key.value}")

                last_key_per_field[key.field] = key

    # finish
    if key:
        last_key = last_key_per_field[key.field] if key.field in last_key_per_field else key
        print("Changed", f"{key.field}={last_key.value}->{key.value}", point_in_times[key])
        times_per_period[last_key].append(point_in_times[last_key])

    durations_per_period = {key: [(value.end_time - value.start_time) for value in values] for key, values in
                            times_per_period.items()}
    total_durations_per_period = {
        key: timedelta(seconds=sum([(value.end_time - value.start_time).total_seconds() for value in values])) for
        key, values in
        times_per_period.items()}

    result = {key: {
        "periods": values,
        "total": total_durations_per_period[key]
    } for key, values in durations_per_period.items()}
    pprint(result)


asyncio.run(get_event_field_value_duration_time("profile-interest", ['type', 'properties.Vacation']))


start_time = datetime(2022, 12, 22, 17, 42, 10, 954105)
end_time = datetime(2022, 12, 22, 17, 42, 53, 10046)
print(end_time-start_time)

start_time = datetime(2022, 12, 22, 17, 42, 10, 954105)
end_time = datetime(2022, 12, 22, 17, 44, 31, 38971)
print(end_time-start_time)