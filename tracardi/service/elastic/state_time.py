import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import List, Optional, Dict, Any, Callable, Tuple
from dateutil import parser
from dotty_dict import dotty

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.driver.elastic import event as event_db

logger = get_logger(__name__)


@dataclass
class PointInTime:
    record: int
    record_span: int
    timestamp: datetime
    field: str
    old: Any
    new: Any
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    def get_duration(self) -> timedelta:
        return self.end_time - self.start_time

    def __repr__(self):
        return f"PointInTime({self.record} {self.field}=\"{self.old} : {self.new}\" " \
               f"duration={self.get_duration()} span={self.record_span})"


@dataclass
class Row:
    timestamp: datetime
    field: str
    value: Any


@dataclass
class Report:
    report: dict
    time_table: Optional[dict] = None


class TimeTable:

    def __init__(self):
        self.change_table = defaultdict(list)
        self.last_change: Dict[str, Tuple[datetime, int]] = {}  # key = field, value = time amd record
        self.last_value: Dict[str, str] = {}  # key = field
        self.last_point_in_time: Dict[str, PointInTime] = {}

    def finish(self, now, record):
        for field, (last_change_time, last_change_record) in self.last_change.items():
            value = self.last_value[field]
            self.add(
                Row(now, field, value),
                PointInTime(
                    record=record,
                    record_span=record - last_change_record,
                    timestamp=now,
                    field=field,
                    start_time=last_change_time,
                    end_time=now,
                    old=value,
                    new=value
                )
            )

    def add(self, row: Row, point_in_time: PointInTime):
        self.change_table[(row.field, row.value)].append(point_in_time)
        logger.debug((row.field, row.value), point_in_time)

    def mark_change(self, row: Row, now: datetime, record: int):
        self.set_last_change(row, now, record)
        self.set_last_value(row)

    def set_last_change(self, row: Row, now: datetime, record: int):
        self.last_change[row.field] = (now, record)

    def get_last_change(self, row) -> Tuple[datetime, int]:
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


def get_durations(change_table, period_functions):
    for key, point_in_times in change_table.items():
        periods = []
        for point_in_time in point_in_times:
            if period_functions and key in period_functions:
                # Filter
                include = period_functions[key](point_in_time)
                print(key, include)
                if include is True:
                    periods.append(point_in_time.get_duration())
            else:
                periods.append(point_in_time.get_duration())
        yield key, periods


def get_total_duration(change_table, period_functions):
    for key, point_in_times in change_table.items():
        periods = []
        for point_in_time in point_in_times:
            if period_functions and key in period_functions:
                # Filter
                include = period_functions[key](point_in_time)
                if include is True:
                    periods.append(point_in_time.get_duration())
            else:
                periods.append(point_in_time.get_duration())
        yield key, timedelta(seconds=sum([duration.total_seconds() for duration in periods]))


async def report_duration_time_per_field(chunk_result, fields: List[str],
                                         field_transformers: Optional[Dict[str, Callable[[Row], str]]] = None,
                                         period_functions: Dict[Tuple[str, Any], Callable[[PointInTime], bool]] = None,
                                         return_time_table=False
                                         ):
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

                if field_transformers and field in field_transformers:
                    value = field_transformers[field](row)
                    if value is None:
                        # Transformer can discard row
                        continue
                    row.value = value

                if not time_table.has_row_in_table(row):
                    time_table.set_last_value(row)
                    time_table.set_last_change(row, now, record_no)

                is_changed = time_table.has_changed(row)

                logger.debug(f"{record_no} {is_changed} {now} {row.field}={row.value} ")

                if is_changed:
                    last_value = time_table.get_last_value(row)
                    last_change_time, last_change_record = time_table.get_last_change(row)
                    time_table.add(
                        Row(timestamp=now, field=row.field, value=last_value),
                        PointInTime(record=record_no,
                                    record_span=record_no - last_change_record,
                                    timestamp=now,
                                    field=row.field,
                                    old=last_value,
                                    new=row.value,
                                    start_time=last_change_time,
                                    end_time=now
                                    )
                    )
                    time_table.mark_change(row, now, record_no)
    if now:
        time_table.finish(now, record_no)

    # Sum results
    durations_per_period = [(key, durations) for key, durations in
                            get_durations(time_table.change_table, period_functions) if durations]
    total_durations_per_period = {key: value for key, value in
                                  get_total_duration(time_table.change_table, period_functions)
                                  if value.total_seconds() > 0}

    result = {key: {
        "periods": values,
        "total": total_durations_per_period[key]
    } for key, values in durations_per_period}

    result = Report(
        report=result
    )

    if return_time_table:
        # todo filter change table with period_functions
        result.time_table = dict(time_table.change_table)

    return result


async def main():
    source_id = None
    event_type = "profile-interest"
    search_by = [('type', event_type)]
    if source_id:
        search_by.append(
            ('source.id', source_id)
        )

    fields = ['context.page.history.length']
    result = event_db.get_all_events_by_fields(search_by, fields + ["metadata.time.insert"])
    transformers = {
        # 'context.page.history.length': lambda row: "a" if row.value > 5 else "b"
    }

    period_functions: Dict[Tuple[str, Any], Callable[[PointInTime], bool]] = {
        ('context.page.history.length', 7): lambda point_in_time: True if point_in_time.record_span > 30 else False
    }
    return await report_duration_time_per_field(result, fields, transformers, period_functions, return_time_table=True)


print(asyncio.run(main()))
