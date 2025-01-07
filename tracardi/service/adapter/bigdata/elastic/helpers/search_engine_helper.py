from typing import List
from lark import LarkError

from datetime import datetime, timedelta
from typing import Tuple, Optional
from tracardi.domain.storage_record import StorageRecords
from tracardi.common.logging.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.client.elastic_index import ElasticIndex
from tracardi.service.list_default_value import list_value_at_index
from tracardi.domain.query_result import QueryResult
from tracardi.domain.time_range_query import DatetimeRangePayload
from tracardi.common.exception.exception import StorageException
from tracardi.service.storage.elastic.parser.query_parser import SqlSearchQueryParser

_logger = get_logger(__name__)


def _timedelta_to_largest_unit(delta: timedelta):
    # Constants
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_DAY = 86400

    total_seconds = delta.total_seconds()

    # Calculate for each unit
    if total_seconds >= SECONDS_PER_DAY:
        days = total_seconds / SECONDS_PER_DAY
        return int(days), 'd', "%y-%m-%d"
    elif total_seconds >= SECONDS_PER_HOUR:
        hours = total_seconds / SECONDS_PER_HOUR
        return int(hours), 'h', "%d/%m %H:%M"
    elif total_seconds >= SECONDS_PER_MINUTE:
        minutes = total_seconds / SECONDS_PER_MINUTE
        return int(minutes), 'm', "%H:%M"
    else:
        return int(total_seconds), 's', "%M"


def _interval(start_date: datetime, end_date: datetime):
    INTERVALS = 30

    # Calculate the total difference in minutes to ensure we cover all cases accurately
    total_seconds = (end_date - start_date).total_seconds()

    interval = timedelta(seconds=int(total_seconds / INTERVALS))

    return _timedelta_to_largest_unit(interval)


class SqlSearchQueryEngine:

    def __init__(self, index: ElasticIndex):
        self._index = index
        self._index_name = index.index_key
        self._sorting_map = {
            'event': [{'metadata.time.insert': 'desc'}],
            'session': [{'metadata.time.insert': 'desc'}],
            'profile': [{'metadata.time.update': 'desc'},
                        {'metadata.time.insert': 'desc'},
                        {'metadata.time.create': 'desc'}],
            'log': [{'date': 'desc'}],
            'entity': [{'metadata.time.insert': 'desc'}],
        }
        self._time_field_map = {
            'event': 'metadata.time.insert',
            'session': 'metadata.time.insert',
            'profile': 'metadata.time.update',
            'log': 'date',
            'entity': 'metadata.time.insert',
        }
        self._parser = SqlSearchQueryParser()

    @staticmethod
    def _convert_time_zone(query, min_date_time, max_date_time) -> Tuple[datetime, datetime, Optional[str]]:
        time_zone = "UTC" if query.timeZone is None or query.timeZone == "" else query.timeZone

        if time_zone != "UTC":
            min_date_time, time_zone = query.convert_to_local_datetime(min_date_time, time_zone)
            max_date_time, time_zone = query.convert_to_local_datetime(max_date_time, time_zone)

        return min_date_time, max_date_time, time_zone

    async def search(self, query: str = None, start: int = 0, limit: int = 20) -> StorageRecords:
        query = self._parser.parse(query)

        if query is None:
            query = {
                "query": {
                    "match_all": {}
                }
            }
        else:
            query = {
                "query": query
            }

        query['from'] = start
        query['size'] = limit

        result = await self._index.query(query)
        return StorageRecords.build_from_elastic(result)

    @staticmethod
    def _string_query(query: DatetimeRangePayload, min_date_time, max_date_time, time_range_field: str, sorting: list,
                      time_zone: str) -> dict:

        es_query = {
            "from": query.start,
            "size": query.limit,
            'sort': sorting,
            "query": {"bool": {"filter": {"range": {
                time_range_field: {
                    'from': min_date_time,
                    'to': max_date_time,
                    'include_lower': True,
                    'include_upper': True,
                    'boost': 1.0,
                    'time_zone': time_zone if time_zone else "UTC"
                }}
            }}}}

        if query.where:
            es_query['query']["bool"]["must"] = {'query_string': {"query": query.where}}

        return es_query

    def _query(self, query: DatetimeRangePayload, min_date_time, max_date_time, time_range_field: str, sorting: list,
               time_zone: str) -> dict:
        query_range = {
            'range': {
                time_range_field: {
                    'from': min_date_time,
                    'to': max_date_time,
                    'include_lower': True,
                    'include_upper': True,
                    'boost': 1.0,
                    'time_zone': time_zone if time_zone else "UTC"
                }
            }
        }

        es_query = {
            "from": query.start,
            "size": query.limit,
            'sort': sorting,
        }

        query_where = self._parser.parse(query.where)

        if query_where is not None:
            es_query['query'] = {
                "bool": {
                    "must": [
                        query_where,
                        query_range
                    ]
                }
            }
        else:
            es_query['query'] = query_range

        return es_query

    async def time_range(self, query: DatetimeRangePayload) -> QueryResult:

        if self._index_name not in self._sorting_map:
            raise ValueError("No time_field available on `{}`".format(self._index_name))

        min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
        min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)

        sorting = self._sorting_map[self._index_name]
        time_field = self._time_field_map[self._index_name]

        try:
            es_query = self._query(query, min_date_time, max_date_time, time_field, sorting, time_zone)
        except LarkError:
            es_query = self._string_query(query, min_date_time, max_date_time, time_field, sorting, time_zone)

        try:
            result = await self._index.query(es_query)
        except StorageException as e:
            _logger.warning(
                "Could not filter data using {}. Possible reason - wrong filter query typed by user. Details: {}".format(
                    es_query, str(e)))
            return QueryResult(total=0, result=[])

        return QueryResult(**result.dict())

    async def histogram(self, query: DatetimeRangePayload, group_by: str = None) -> QueryResult:

        def __format_count(data, unit, interval, format):
            for row in data:
                # todo timestamp no timezone
                timestamp = datetime.fromisoformat(row["key_as_string"].replace('Z', '+00:00'))
                speed = int(row["doc_count"]) / interval
                yield {
                    "date": "{}".format(timestamp.strftime(format)),
                    'interval': "+{}{}".format(interval, unit),
                    "count": row["doc_count"],
                    "speed": f"{speed:.3f}/{unit}"
                }

        def __format_count_by_bucket(data, unit, interval, format):

            result = []
            buckets = []
            for bucket in data:
                bucket_name = bucket['key'].lower()
                buckets.append(bucket_name)

                # Each bucket must have the same number of items
                for number, row in enumerate(bucket['items_over_time']['buckets']):
                    # todo timestamp no timezone
                    timestamp = datetime.fromisoformat(row["key_as_string"].replace('Z', '+00:00'))
                    speed = int(row["doc_count"]) / interval
                    item, result = list_value_at_index(result, number, default_value={
                        "date": "{}".format(timestamp.strftime(format)),
                        'interval': "+{}{}".format(interval, unit),
                        "speed": f"{speed:.3f}/{unit}"
                    })

                    item[bucket_name] = row["doc_count"]
                    result[number] = item

            return result, buckets

        min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
        min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)

        # sql = query.where
        sorting = self._sorting_map[self._index_name]
        time_field = self._time_field_map[self._index_name]

        interval, unit, format = _interval(min_date_time, max_date_time)
        try:
            es_query = self._query(query, min_date_time, max_date_time, time_field, sorting, time_zone)
        except LarkError:
            es_query = self._string_query(query, min_date_time, max_date_time, time_field, sorting, time_zone)

        if group_by is None:
            es_query = {
                "size": 0,
                "query": es_query['query'],
                "aggs": {
                    "items_over_time": {
                        "date_histogram": {
                            "min_doc_count": 0,
                            "field": time_field,
                            "fixed_interval": f"{interval}{unit}",
                            "extended_bounds": {
                                "min": min_date_time,
                                "max": max_date_time
                            }
                        }
                    }
                }
            }
            if time_zone:
                es_query['aggs']['items_over_time']['date_histogram']['time_zone'] = time_zone

            try:
                result = await self._index.query(es_query)
            except StorageException as e:
                _logger.error("Could not query {}. Reason: {}".format(es_query, str(e)))
                return QueryResult(total=0, result=[])

            try:

                qs = {
                    'total': result.total,
                    'result': list(
                        __format_count(result.aggregations('items_over_time').buckets(), unit, interval, format)),
                    'buckets': ['count']
                }

                return QueryResult(**qs)

            except KeyError:
                # When no result
                qs = {
                    'total': 0,
                    'result': []
                }

            return QueryResult(**qs)

        else:

            es_query = {
                "size": 0,
                "query": es_query['query'],
                "aggs": {
                    "by_field": {
                        "terms": {
                            "field": group_by,
                            "order": {
                                "_count": "desc"
                            },
                            "size": 5
                        },
                        "aggs": {
                            "items_over_time": {
                                "date_histogram": {
                                    "min_doc_count": 0,
                                    "field": time_field,
                                    "fixed_interval": f"{interval}{unit}",
                                    "extended_bounds": {
                                        "min": min_date_time,
                                        "max": max_date_time
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if time_zone:
                es_query['aggs']['by_field']['aggs']['items_over_time']['date_histogram']['time_zone'] = time_zone

            try:
                result = await self._index.query(es_query)
            except StorageException as e:
                _logger.error("Could not query {}. Reason: {}".format(es_query, str(e)))
                return QueryResult(total=0, result=[])

            try:

                buckets_result, buckets = __format_count_by_bucket(result.aggregations('by_field').buckets(), unit,
                                                                   interval, format)
                qs = {
                    'total': result.total,
                    'result': buckets_result,
                    'buckets': buckets

                }

                return QueryResult(**qs)

            except KeyError:
                # When no result
                qs = {
                    'total': 0,
                    'result': []
                }

            return QueryResult(**qs)


def _find_time_fields(mapping, field_types: List[str], prefix=''):
    time_fields = []
    for field, properties in mapping.items():
        if 'type' in properties and properties['type'] in field_types:
            time_fields.append(f"{prefix}.{field}" if prefix else field)
        if 'properties' in properties:
            subfields = _find_time_fields(properties['properties'],
                                          field_types,
                                          prefix=f"{prefix}.{field}" if prefix else field)
            time_fields.extend(subfields)
    return time_fields


def get_fields_of_given_field_type(mapping, types: List[str]):
    time_fields = []
    if filter is not None:
        time_fields = _find_time_fields(mapping['mappings']['properties'], types)
    return time_fields