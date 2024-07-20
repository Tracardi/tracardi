import elasticsearch
from lark import LarkError
from pydantic import BaseModel

import tracardi.service.storage.elastic.driver.elastic_storage as storage
from typing import List, Union, Dict

from tracardi.domain.entity import Entity
from tracardi.domain.storage.index_mapping import IndexMapping
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from datetime import datetime, timedelta
from typing import Tuple, Optional
from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.list_default_value import list_value_at_index
from tracardi.service.singleton import Singleton
from tracardi.domain.query_result import QueryResult
from tracardi.domain.time_range_query import DatetimeRangePayload
from tracardi.exceptions.exception import StorageException
from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.transformer.filter_transformer import FilterTransformer
from tracardi.service.storage.elastic.driver.elastic_storage import ElasticStorage

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


class SqlSearchQueryParser(metaclass=Singleton):
    def __init__(self):
        self.parser = Parser(Parser.read('grammar/filter_condition.lark'), start='expr')

    def parse(self, query) -> Optional[dict]:
        if not query:
            return None

        tree = self.parser.parse(query)
        result = FilterTransformer().transform(tree)
        return result


class SqlSearchQueryEngine:

    def __init__(self, persister):
        self.persister = persister  # type: PersistenceService
        self.index = persister.storage.index_key
        self.sorting_map = {
            'event': [{'metadata.time.insert': 'desc'}],
            'session': [{'metadata.time.insert': 'desc'}],
            'profile': [{'metadata.time.update': 'desc'}, {'metadata.time.insert': 'desc'},
                        {'metadata.time.create': 'desc'}],
            'log': [{'date': 'desc'}],
            'entity': [{'metadata.time.insert': 'desc'}],
        }
        self.time_field_map = {
            'event': 'metadata.time.insert',
            'session': 'metadata.time.insert',
            'profile': 'metadata.time.update',
            'log': 'date',
            'entity': 'metadata.time.insert',
        }
        self.parser = SqlSearchQueryParser()

    @staticmethod
    def _convert_time_zone(query, min_date_time, max_date_time) -> Tuple[datetime, datetime, Optional[str]]:
        time_zone = "UTC" if query.timeZone is None or query.timeZone == "" else query.timeZone

        if time_zone != "UTC":
            min_date_time, time_zone = query.convert_to_local_datetime(min_date_time, time_zone)
            max_date_time, time_zone = query.convert_to_local_datetime(max_date_time, time_zone)

        return min_date_time, max_date_time, time_zone

    async def search(self, query: str = None, start: int = 0, limit: int = 20) -> StorageRecords:
        query = self.parser.parse(query)

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

        result = await self.persister.query(query)
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

        query_where = self.parser.parse(query.where)

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

        if self.index not in self.sorting_map:
            raise ValueError("No time_field available on `{}`".format(self.index))

        min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
        min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)

        sorting = self.sorting_map[self.index]
        time_field = self.time_field_map[self.index]

        try:
            es_query = self._query(query, min_date_time, max_date_time, time_field, sorting, time_zone)
        except LarkError:
            es_query = self._string_query(query, min_date_time, max_date_time, time_field, sorting, time_zone)

        try:
            result = await self.persister.filter(es_query)
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
        sorting = self.sorting_map[self.index]
        time_field = self.time_field_map[self.index]

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
                result = await self.persister.query(es_query)
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
                result = await self.persister.query(es_query)
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


class PersistenceService:

    def __init__(self, storage: ElasticStorage):
        self.storage = storage

    def get_single_storage_index(self) -> str:
        """
        This is needed for delete operation
        """
        return self.storage.index.get_single_storage_index()

    def get_current_multi_storage_index(self) -> str:
        """
        This is needed for delete operation
        """
        return self.storage.index.get_current_multi_storage_index()

    def get_multi_storage_alias(self) -> str:
        return self.storage.index.get_multi_storage_alias()

    async def exists(self, id: str) -> bool:
        try:
            return await self.storage.exists(id)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def load(self, id: str) -> Optional[StorageRecord]:
        try:
            return await self.storage.load(id)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    def scan(self, query: dict = None, batch: int = 1000):
        try:
            return self.storage.scan(query, batch)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def count(self, query: dict) -> dict:
        try:
            return await self.storage.count(query)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def get_mapping(self) -> IndexMapping:
        try:
            return IndexMapping(await self.storage.get_mapping(self.storage.index.get_index_alias()))
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def set_mapping(self, index: str, mapping: dict):
        try:
            return await self.storage.set_mapping(index, mapping)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def load_by(self, field: str, value: Union[str, int, float, bool], limit: int = 100,
                      sort: List[Dict[str, Dict]] = None) -> StorageRecords:
        try:
            return await self.storage.load_by(field, value, limit, sort)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def load_by_query_string(self, query_string: str, limit: int = 100) -> StorageRecords:
        try:
            return await self.storage.load_by_query_string(query_string, limit)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def match_by(self, field: str, value: str, limit: int = 100) -> StorageRecords:
        try:
            return await self.storage.match_by(field, value, limit)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def load_by_values(self, field_value_pairs: List[tuple],
                             sort_by: Optional[List[storage.ElasticFiledSort]] = None,
                             limit=1000,
                             condition='must'
                             ) -> StorageRecords:
        try:
            return await self.storage.load_by_values(field_value_pairs, sort_by, limit=limit, condition=condition)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def delete_by(self, field: str, value: str, index: str = None) -> dict:
        try:
            return await self.storage.delete_by(field, value, index)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def load_all(self, start: int = 0, limit: int = 100, sort: List[Dict[str, Dict]] = None) -> StorageRecords:
        try:
            query = {
                "from": start,
                "size": limit,
                "query": {
                    "match_all": {}
                }
            }

            if sort is not None:
                query['sort'] = sort
            return await self.storage.search(query)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def upsert(self, data: Union[StorageRecord, Entity, BaseModel, dict, list, set],
                     replace_id: bool = True, exclude=None) -> BulkInsertResult:
        try:
            return await self.storage.create(data, replace_id=replace_id, exclude=exclude)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def delete(self, id: str, index: str) -> dict:
        try:
            return await self.storage.delete(id, index=index)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def bulk_delete(self, ids: List[str]) -> dict:
        try:
            return await self.storage.bulk_delete(ids)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def filter(self, query: dict) -> StorageRecords:
        try:
            return await self.storage.search(query)
        except elasticsearch.exceptions.NotFoundError:
            _logger.warning("No result found for query {}".format(query))
            return StorageRecords.build_from_elastic()
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def aggregate(self, query: dict, aggregate_key='key') -> StorageAggregateResult:
        try:
            return StorageAggregateResult(await self.storage.search(query), aggregate_key)
        except elasticsearch.exceptions.NotFoundError:
            _logger.warning("No result found for query {}".format(query))
            return StorageAggregateResult()
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def query(self, query, logg_error=True) -> StorageRecords:
        try:
            return await self.storage.search(query)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if logg_error:
                _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def refresh(self, params=None, headers=None):
        try:
            return await self.storage.refresh(params, headers)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def flush(self, params=None, headers=None):
        try:
            return await self.storage.flush(params, headers)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def query_by_sql(self, query: str, start: int = 0, limit: int = 0) -> StorageRecords:
        engine = SqlSearchQueryEngine(self)
        return await engine.search(query, start, limit)

    async def query_by_sql_in_time_range(self, query: DatetimeRangePayload) -> QueryResult:
        engine = SqlSearchQueryEngine(self)
        return await engine.time_range(query)

    async def histogram_by_sql_in_time_range(self, query: DatetimeRangePayload, group_by: str = None) -> QueryResult:
        engine = SqlSearchQueryEngine(self)
        return await engine.histogram(query, group_by)

    async def update_by_query(self, query: dict, conflicts: str = 'abort', wait_for_completion: bool = None):
        try:
            return await self.storage.update_by_query(
                query=query,
                conflicts=conflicts,
                wait_for_completion=wait_for_completion
            )
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def update_by_id(self, id: str, record: dict, index: str, retry_on_conflict=3):
        try:
            return await self.storage.update(id, record=record, index=index, retry_on_conflict=retry_on_conflict)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e), details=str(e))

    async def delete_by_query(self, query: dict):
        try:
            return await self.storage.delete_by_query(query=query)
        except elasticsearch.exceptions.ElasticsearchException as e:
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))
