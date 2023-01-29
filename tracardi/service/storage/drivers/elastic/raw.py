from typing import List, Optional
from elasticsearch import NotFoundError
from tracardi.domain.storage_record import StorageRecords
from tracardi.event_server.utils.memory_cache import CacheItem, MemoryCache
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.elastic_storage import ElasticFiledSort
from tracardi.service.storage.factory import storage_manager
from tracardi.service.storage.index import resources
from tracardi.service.storage.persistence_service import PersistenceService

memory_cache = MemoryCache("index-mapping")


def index(idx) -> PersistenceService:
    return storage_manager(idx)


async def query(index: str, query: dict) -> StorageRecords:
    return await storage_manager(index).query(query)


async def load_by_key_value_pairs(index, key_value_pairs: List[tuple], sort_by: Optional[List[ElasticFiledSort]] = None,
                                  limit: int = 20) -> StorageRecords:
    return await storage_manager(index).load_by_values(key_value_pairs, sort_by, limit=limit)


async def update_profile_ids(index: str, old_profile_id: str, merged_profile_id):
    query = {
        "script": {
            "source": f"ctx._source.profile.id = '{merged_profile_id}'",
            "lang": "painless"
        },
        "query": {
            "term": {
                "profile.id": old_profile_id
            }
        }
    }

    return await storage_manager(index=index).update_by_query(query=query)


async def count_by_query(index: str, query: str, time_span: int) -> StorageRecords:
    result = await storage_manager(index).storage.count_by_query_string(
        query,
        f"{time_span}s" if time_span < 0 else ""
    )
    return result


async def count_all_indices_by_alias(prefix: str = None):
    """
    Missing indices are returned as count = 0
    """

    for name, index in resources.resources.items():
        try:
            sm = storage_manager(name)
            count = await sm.storage.count(prefix=prefix)
            yield name, count['count']
        except NotFoundError:
            yield name, 0


def _acknowledged(result):
    return 'acknowledged' in result and result['acknowledged'] is True


async def remove_alias(alias_index):
    es = ElasticClient.instance()
    if await es.exists_alias(alias_index, index=None):
        result = await es.delete_alias(alias=alias_index, index="_all")
        if _acknowledged(result):
            return True
    return False


async def update_aliases(query):
    es = ElasticClient.instance()
    return await es.update_aliases(query)


async def remove_template(template_name):
    es = ElasticClient.instance()
    if await es.exists_index_template(template_name):
        result = await es.delete_index_template(template_name)
        if not _acknowledged(result):
            return False
    return True


async def add_template(template_name, map) -> bool:
    es = ElasticClient.instance()
    result = await es.put_index_template(template_name, map)
    return _acknowledged(result)


async def indices():
    es = ElasticClient.instance()
    return await es.list_indices()


async def health():
    es = ElasticClient.instance()
    return await es.cluster.health()


async def aliases():
    es = ElasticClient.instance()
    return await es.list_aliases()


async def clone(source_index, destination_index):
    es = ElasticClient.instance()
    return await es.clone(source_index, destination_index)


async def exists_index(index):
    es = ElasticClient.instance()
    return await es.exists_index(index)


async def exists_alias(alias, index):
    es = ElasticClient.instance()
    return await es.exists_alias(alias, index=index)


async def reindex(source, destination, wait_for_completion=True):
    es = ElasticClient.instance()
    return await es.reindex(source, destination, wait_for_completion)


async def task_status(task_id):
    es = ElasticClient.instance()
    return await es._client.tasks.get(task_id)


async def refresh(index):
    es = ElasticClient.instance()
    return await es.refresh(index)


async def get_mapping(index):
    es = ElasticClient.instance()
    result = await es.get_mapping(index)
    return result[index]


async def set_mapping(index: str, mapping: dict):
    es = ElasticClient.instance()
    return await es.set_mapping(index, mapping)


async def create_index(index: str, mapping: dict) -> bool:
    es = ElasticClient.instance()
    result = await es.create_index(index, mapping)
    return _acknowledged(result)


async def get_unique_field_values(index, field, limit=50):
    es = ElasticClient.instance()
    query = {
        "size": 0,
        "aggs": {
            "fields": {
                "terms": {"field": field, "size": limit}
            }
        }}
    index = resources[index]
    return StorageRecords.build_from_elastic(await es.search(index.get_index_alias(), query))


async def get_mapping_fields(index) -> list:
    memory_key = f"{index}-mapping-cache"
    if memory_key not in memory_cache:
        mapping = await storage_manager(index).get_mapping()
        fields = mapping.get_field_names()
        memory_cache[memory_key] = CacheItem(data=fields, ttl=5)  # result is cached for 5 seconds
    return memory_cache[memory_key].data
