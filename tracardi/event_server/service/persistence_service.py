from typing import List

import elasticsearch
import logging
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.exceptions.exception import StorageException
import tracardi.service.storage.elastic_storage as storage
from tracardi.domain.storage_result import StorageResult

_logger = logging.getLogger("PersistenceService")


class PersistenceService:

    def __init__(self, storage: storage.ElasticStorage):
        self.storage = storage

    async def load(self, id: str):
        try:
            return await self.storage.load(id)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def load_by(self, field: str, value: str) -> StorageResult:
        try:
            return StorageResult(await self.storage.load_by(field, value))
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def load_by_values(self, field_value_pairs: List[tuple], limit=1000) -> StorageResult:
        try:
            return StorageResult(await self.storage.load_by_values(field_value_pairs, limit))
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def delete_by(self, field: str, value: str) -> dict:
        try:
            return await self.storage.delete_by(field, value)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def load_all(self) -> StorageResult:
        try:
            query = {
                "size": 100,
                "query": {
                    "match_all": {}
                }
            }
            result = await self.storage.search(query)
            return StorageResult(result)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def upsert(self, data) -> BulkInsertResult:
        try:

            if not isinstance(data, list):
                if 'id' in data:
                    data["_id"] = data['id']
                payload = [data]
            else:
                # Add id
                for d in data:
                    if 'id' in d:
                        d["_id"] = d['id']
                payload = data

            return await self.storage.create(payload)

        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def delete(self, id: str) -> dict:
        try:
            return await self.storage.delete(id)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def filter(self, query: dict) -> StorageResult:
        try:
            return StorageResult(await self.storage.search(query))
        except elasticsearch.exceptions.NotFoundError:
            _logger.warning("No result found for query {}".format(query))
            return StorageResult()
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def query(self, query):
        try:
            return await self.storage.search(query)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def translate(self, sql):
        try:
            return await self.storage.translate(sql)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def refresh(self, params=None, headers=None):
        try:
            return await self.storage.refresh(params, headers)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def flush(self, params=None, headers=None):
        try:
            return await self.storage.flush(params, headers)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def sql(self, sql):
        try:
            query = await self.storage.translate(sql)
            if '_source' in query and query['_source'] == False:
                query['_source'] = True
            return StorageResult(await self.storage.search(query))
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))
