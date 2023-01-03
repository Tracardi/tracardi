import asyncio
import logging
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Optional, Dict, Any
from dateutil import parser
from dotty_dict import dotty

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver import storage

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


@dataclass
class PointInTime:
    pos: int
    timestamp: datetime
    field: str
    old: Any
    new: Any
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    def get_duration(self) -> timedelta:
        return self.end_time - self.start_time

    def __repr__(self):
        return f"PointInTime({self.pos} {self.field}=\"{self.old} : {self.new}\" {self.start_time} - {self.end_time})"


Row = namedtuple("EventAndValue", "timestamp field value")


class TimeTable:

    def __init__(self):
        self.change_table = defaultdict(list)
        self.last_change: Dict[str, datetime] = {}  # key = field
        self.last_value: Dict[str, str] = {}  # key = field
        self.last_point_in_time: Dict[str, PointInTime] = {}

    def finish(self, now):
        for field, start_time in self.last_change.items():
            value = self.last_value[field]
            self.add(
                Row(now, field, value),
                PointInTime(
                    pos=0,
                    timestamp=now,
                    field=field,
                    start_time=start_time,
                    end_time=now,
                    old=value,
                    new=value
                )
            )

    def add(self, row: Row, point_in_time: PointInTime):
        self.change_table[(row.field, row.value)].append(point_in_time)

    def mark_change(self, row: Row, now: datetime):
        self.set_last_change(row, now)
        self.set_last_value(row)

    def set_last_change(self, row: Row, now: datetime):
        self.last_change[row.field] = now

    def get_last_change(self, row) -> datetime:
        return self.last_change[row.field]

    def set_last_value(self, row: Row):
        self.last_value[row.field] = row.value

    def get_last_value(self, row: Row) -> Any:
        return self.last_value[row.field]

    def has_row_in_table(self, row: Row):
        return row.field in self.last_value

    def has_changed(self, row: Row) -> bool:
        if not self.has_row_in_table(row):
            raise ValueError("Set initial value")
        return row.value != self.last_value[row.field]


async def report_duration_time_per_field(chunk_result, fields: List[str]):
    record_no = 0
    chunk_no = 0

    time_table = TimeTable()

    now = None

    async for result in chunk_result:
        chunk_no += 1

        for event in result:

            flat_event = dotty(event)
            record_no += 1
            for field in fields:

                now = parser.parse(event['metadata']['time']['insert'])

                try:
                    value = flat_event[field]
                except KeyError:
                    continue

                row = Row(now, field, value)

                if not time_table.has_row_in_table(row):
                    time_table.set_last_value(row)
                    time_table.set_last_change(row, now)

                is_changed = time_table.has_changed(row)

                logger.debug(f"{record_no} {is_changed} {now} {row.field}={row.value} ")

                if is_changed:
                    time_table.add(
                        row,
                        PointInTime(record_no,
                                    now,
                                    field=row.field,
                                    old=time_table.get_last_value(row),
                                    new=row.value,
                                    start_time=time_table.get_last_change(row),
                                    end_time=now
                                    )
                    )
                    time_table.mark_change(row, now)
    if now:
        time_table.finish(now)

    # Sum results

    durations_per_period = {key: [point_in_time.get_duration() for point_in_time in point_in_times] for
                            key, point_in_times in time_table.change_table.items()}
    total_durations_per_period = {
        key: timedelta(seconds=sum([point_in_time.get_duration().total_seconds() for point_in_time in point_in_times]))
        for key, point_in_times in time_table.change_table.items()}

    result = {key: {
        "periods": values,
        "total": total_durations_per_period[key]
    } for key, values in durations_per_period.items()}

    return result


async def main():
    source_id = None
    event_type = "profile-interest"
    search_by = [('type', event_type)]
    if source_id:
        search_by.append(
            ('source.id', source_id)
        )

    fields = ['type', 'properties.Vacation']
    result = storage.driver.event.get_all_events_by_fields(search_by, fields + ["metadata.time.insert"])

    return await report_duration_time_per_field(result, fields)


print(asyncio.run(main()))

# start_time = datetime(2022, 12, 22, 17, 42, 10, 954105)
# end_time = datetime(2022, 12, 22, 17, 42, 53, 10046)
# print(end_time - start_time)
#
# start_time = datetime(2022, 12, 22, 17, 44, 31, 38971)
# end_time = datetime(2023, 1, 2, 0, 13, 20, 393175)
# print(end_time - start_time)
