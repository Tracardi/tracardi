import elasticsearch
from pydantic import BaseModel

from tracardi.event_server.service.persistence_service import PersistenceService
from tracardi.domain.agg_result import AggResult
from tracardi.domain.storage_result import StorageResult
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.exceptions.exception import TracardiException, StorageException
from tracardi.service.storage.elastic_storage import ElasticStorage


class CollectionCrud:

    def __init__(self, index, payload):
        self.payload = payload
        self.index = index
        self.storage = PersistenceService(ElasticStorage(index_key=self.index))

    async def save(self) -> BulkInsertResult:
        try:
            if not isinstance(self.payload, list):
                raise TracardiException("CollectionCrud dave payload must be list.")
            data = [p.dict() for p in self.payload if isinstance(p, BaseModel)]
            return await self.storage.upsert(data)

        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def load(self) -> StorageResult:
        try:

            return await self.storage.load_all()

        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def uniq_field_value(self, field) -> AggResult:
        try:
            query = {
                "size": "0",
                "aggs": {
                    "uniq": {
                        "terms": {
                            "field": field
                        }
                    }
                }
            }
            return AggResult('uniq', await self.storage.query(query), return_counts=False)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))
