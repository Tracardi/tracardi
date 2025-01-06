from typing import Union, List, Set, Optional

from tracardi.config import elastic
from tracardi.domain.entity import FlatEntity
from tracardi.domain.storage_record import StorageRecord, StorageRecords

from tracardi.service.adapter.bigdata.elastic.client.elastic_client import ElasticClient
from tracardi.service.adapter.bigdata.elastic.client.elastic_index import ElasticIndex
from tracardi.service.adapter.bigdata.elastic.client.elastic_template import ElasticTemplate


class ElasticCoreAdapter:

    def __init__(self, client: ElasticClient, params: dict):
        self._client = client
        self._params = params

    def _index(self, index) -> ElasticIndex:
        return ElasticIndex(self._client, index)

    async def refresh(self, index_type: str):
        return await self._index(index_type).refresh()

    async def flush(self, index_type: str):
        return await self._index(index_type).flush()

    async def load(self, index_type: str, id: str, **kwargs) -> Optional[StorageRecord]:
        entity_index = self._index(index_type)
        session_record = await entity_index.load(id)

        if session_record is None:
            return None

        return session_record

    async def save(self, index_type: str, entities: Union[FlatEntity, List[FlatEntity], Set[FlatEntity]], **kwargs):
        entity_index = self._index(index_type)
        result = await entity_index.save(entities, exclude={"operation": ...})
        if kwargs.get('refresh_after_save', False):
            await entity_index.flush()
        return result

    async def delete(self, index_type: str, id: str, idx: str, **kwargs):
        entity_index = self._index(index_type)
        result = await entity_index.delete(id, idx)
        if kwargs.get('refresh_after_save', False):
            await entity_index.flush()
        return result

    async def update(self, index_type: str, query: dict, **kwargs):
        entity_index = self._index(index_type)
        return await entity_index.update_by_query(
            query=query,
            **kwargs
        )

    async def query(self, index_type: str, query: dict) -> StorageRecords:
        return await self._index(index_type).query(query)

    async def count(self, index_type: str, query: Optional[dict] = None):
        entity_index = self._index(index_type)
        return await entity_index.count(query)


class ElasticAdapter:

    def __init__(self):
        kwargs = ElasticClient.get_elastic_config(elastic)
        self._client = ElasticClient(**kwargs)
        self._params = {}
        self.core: ElasticCoreAdapter = ElasticCoreAdapter(self._client, self._params)

    def index(self, index) -> ElasticIndex:
        return ElasticIndex(self._client, index)

    @property
    def client(self):
        return self._client

    @property
    def template(self) -> ElasticTemplate:
        return ElasticTemplate(self._client)
