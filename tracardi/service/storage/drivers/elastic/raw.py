from tracardi.domain.storage_record import StorageRecords
from tracardi.event_server.utils.memory_cache import CacheItem, MemoryCache
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.factory import storage_manager
from tracardi.service.storage.index import resources
from tracardi.service.storage.persistence_service import PersistenceService

memory_cache = MemoryCache("index-mapping")


def index(idx) -> PersistenceService:
    return storage_manager(idx)


async def query(index: str, query: dict) -> StorageRecords:
    return await storage_manager(index).query(query)


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


async def create_index(index: str, mapping: dict):
    es = ElasticClient.instance()
    return await es.create_index(index, mapping)


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
