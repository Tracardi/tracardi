import elasticsearch
from pydantic import BaseModel

import tracardi.service.storage.elastic.driver.elastic_storage as storage
from typing import List, Union, Dict

from tracardi.domain.entity import Entity
from tracardi.domain.storage.index_mapping import IndexMapping
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from typing import Optional
from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.exceptions.log_handler import get_logger
# from tracardi.domain.query_result import QueryResult
# from tracardi.domain.time_range_query import DatetimeRangePayload
from tracardi.exceptions.exception import StorageException
from tracardi.service.storage.elastic.driver.elastic_storage import ElasticStorage
# from tracardi.service.storage.elastic.driver.search_engine import SqlSearchQueryEngine

_logger = get_logger(__name__)


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

    # async def search_with_query(self, query: str, start: int = 0, limit: int = 0) -> StorageRecords:
    #     engine = SqlSearchQueryEngine(self)
    #     return await engine.search(query, start, limit)
    #
    # async def search_in_time_range(self, query: DatetimeRangePayload) -> QueryResult:
    #     engine = SqlSearchQueryEngine(self)
    #     return await engine.time_range(query)
    #
    # async def search_histogram_in_time_range(self, query: DatetimeRangePayload, group_by: str = None) -> QueryResult:
    #     engine = SqlSearchQueryEngine(self)
    #     return await engine.histogram(query, group_by)

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
