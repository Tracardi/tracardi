import logging
import elasticsearch
from pydantic import BaseModel

import tracardi.service.storage.elastic_storage as storage
from typing import List, Union, Dict

from tracardi.config import tracardi
from tracardi.domain.entity import Entity
from tracardi.domain.storage.index_mapping import IndexMapping
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from datetime import datetime
from typing import Tuple, Optional
from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.list_default_value import list_value_at_index
from tracardi.service.singleton import Singleton
from tracardi.domain.query_result import QueryResult
from tracardi.domain.time_range_query import DatetimeRangePayload
from tracardi.exceptions.exception import StorageException
from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.transformer.filter_transformer import FilterTransformer
from tracardi.service.storage.elastic_storage import ElasticStorage

_logger = logging.getLogger(__name__)
_logger.setLevel(tracardi.logging_level)
_logger.addHandler(log_handler)


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
        self.time_fields_map = {
            'event': 'metadata.time.insert',
            'session': 'metadata.time.insert',
            'profile': 'metadata.time.insert',
            'log': 'date',
            'entity': 'timestamp'
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
    def _string_query(query: DatetimeRangePayload, min_date_time, max_date_time, time_field: str,
                      time_zone: str) -> dict:

        es_query = {
            "from": query.start,
            "size": query.limit,
            'sort': [{time_field: 'desc'}],
            "query": {"bool": {"filter": {"range": {
                time_field: {
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

    def _query(self, query: DatetimeRangePayload, min_date_time, max_date_time, time_field: str,
               time_zone: str) -> dict:
        query_range = {
            'range': {
                time_field: {
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
            'sort': [{time_field: 'desc'}],
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

    async def time_range(self, query: DatetimeRangePayload, query_type: str = "tql") -> QueryResult:

        if self.index not in self.time_fields_map:
            raise ValueError("No time_field available on `{}`".format(self.index))

        min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
        min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)

        time_field = self.time_fields_map[self.index]
        if query_type == "tql":
            es_query = self._query(query, min_date_time, max_date_time, time_field, time_zone)
        else:
            es_query = self._string_query(query, min_date_time, max_date_time, time_field, time_zone)
        try:
            result = await self.persister.filter(es_query)
        except StorageException as e:
            _logger.error("Could not filter {}. Reason: {}".format(es_query, str(e)))
            return QueryResult(total=0, result=[])

        return QueryResult(**result.dict())

    async def histogram(self, query: DatetimeRangePayload, query_type, group_by: str = None) -> QueryResult:

        def __interval(min: datetime, max: datetime):

            max_interval = 50
            min_interval = 20

            span = max - min

            if span.days > max_interval:
                # up
                return int(span.days / max_interval), 'd', "%y-%m-%d"
            elif min_interval > span.days:
                # down
                interval = int((span.days * 24) / max_interval)
                if interval > 0:
                    return interval, 'h', "%d/%m %H:%M"

                # minutes
                interval = int((span.days * 24 * 60) / max_interval)
                if interval > 0:
                    return interval, 'm', "%H:%M"

                return 1, 'm', "%H:%M"

            return 1, 'd', "%y-%m-%d"

        def __format_count(data, unit, interval, format):
            for row in data:
                # todo timestamp no timezone
                timestamp = datetime.fromisoformat(row["key_as_string"].replace('Z', '+00:00'))
                yield {
                    "date": "{}".format(timestamp.strftime(format)),
                    'interval': "+{}{}".format(interval, unit),
                    "count": row["doc_count"]
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

                    item, result = list_value_at_index(result, number, default_value={
                        "date": "{}".format(timestamp.strftime(format)),
                        'interval': "+{}{}".format(interval, unit),
                    })

                    item[bucket_name] = row["doc_count"]
                    result[number] = item

            return result, buckets

        min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
        min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)

        # sql = query.where
        time_field = self.time_fields_map[self.index]

        interval, unit, format = __interval(min_date_time, max_date_time)

        if query_type == "tql":
            es_query = self._query(query, min_date_time, max_date_time, time_field, time_zone)
        else:
            es_query = self._string_query(query, min_date_time, max_date_time, time_field, time_zone)

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

            except KeyError as e:
                # When no result
                qs = {
                    'total': 0,
                    'result': []
                }

            return QueryResult(**qs)


class PersistenceService:

    def __init__(self, storage: ElasticStorage):
        self.storage = storage

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

    def scan(self, query: dict = None):
        try:
            return self.storage.scan(query)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def count(self, query: dict):
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
                             sort_by: Optional[List[storage.ElasticFiledSort]] = None, limit=1000) -> StorageRecords:
        try:
            return await self.storage.load_by_values(field_value_pairs, sort_by, limit=limit)
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

    async def upsert(self, data: Union[StorageRecord, Entity, BaseModel, dict, list],
                     replace_id: bool = True, exclude=None) -> BulkInsertResult:
        try:
            return await self.storage.create(data, replace_id=replace_id, exclude=exclude)
        except elasticsearch.exceptions.ElasticsearchException as e:
            _logger.error(str(e))
            if len(e.args) == 2:
                message, details = e.args
                raise StorageException(str(e), message=message, details=details)
            raise StorageException(str(e))

    async def delete(self, id: str, index: str = None) -> dict:
        try:
            return await self.storage.delete(id, index=index)
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

    async def query(self, query) -> StorageRecords:
        try:
            return await self.storage.search(query)
        except elasticsearch.exceptions.ElasticsearchException as e:
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

    async def query_by_sql_in_time_range(self, query: DatetimeRangePayload, query_type="tql") -> QueryResult:
        engine = SqlSearchQueryEngine(self)
        return await engine.time_range(query, query_type)

    async def histogram_by_sql_in_time_range(self, query: DatetimeRangePayload, query_type: str = "tql",
                                             group_by: str = None) -> QueryResult:
        engine = SqlSearchQueryEngine(self)
        return await engine.histogram(query, query_type, group_by)

    async def update_by_query(self, query: dict):
        try:
            return await self.storage.update_by_query(query=query)
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
