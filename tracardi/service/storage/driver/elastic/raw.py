from typing import List, Optional, Tuple
from elasticsearch import NotFoundError
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.cache.field_mapping import load_fields
from tracardi.service.field_mappings_cache import FieldMapper
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.elastic_storage import ElasticFiledSort
from tracardi.service.storage.factory import storage_manager
from tracardi.service.storage.index import Resource
from tracardi.service.storage.persistence_service import PersistenceService


def index(idx) -> PersistenceService:
    return storage_manager(idx)


async def query(index: str, query: dict):
    es = ElasticClient.instance()
    return await es.search(index, query)


async def query_by_index(index: str, query: dict) -> StorageRecords:
    return await storage_manager(index).query(query)


async def load_by_id(index: str, id: str) -> StorageRecords:
    query = {
        "query": {
            "term": {
                '_id': id
            }
        }
    }
    es = ElasticClient.instance()
    result = await es.search(index, query)
    return StorageRecords.build_from_elastic(result)


async def load_all(index: str) -> StorageRecords:
    query = {
        "query": {
            "match_all": {}
        }
    }
    es = ElasticClient.instance()
    result = await es.search(index, query)
    return StorageRecords.build_from_elastic(result)


async def delete_by_id(index: str, id: str) -> dict:
    es = ElasticClient.instance()
    return await es.delete(index, id)


async def delete_by_query(index: str, query: str) -> dict:
    es = ElasticClient.instance()
    return await es.delete_by_query(index, query)


async def upsert(index: str, data: dict) -> BulkInsertResult:
    es = ElasticClient.instance()
    return await es.insert(index, [data])


async def bulk_upsert(index: str, data: list) -> BulkInsertResult:
    es = ElasticClient.instance()
    return await es.insert(index, data)


async def load_by_key_value_pairs(index, key_value_pairs: List[tuple], sort_by: Optional[List[ElasticFiledSort]] = None,
                                  limit: int = 20) -> StorageRecords:
    return await storage_manager(index).load_by_values(key_value_pairs, sort_by, limit=limit)


async def update_profile_ids(index: str, old_profile_id: str, merged_profile_id):
    query = {
        "script": {
            "source": "ctx._source.profile.id = params.merged_profile_id",
            "lang": "painless",
            "params": {
                "merged_profile_id": f"{merged_profile_id}"
            }
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


async def count_all_indices_by_alias():
    """
    Missing indices are returned as count = 0
    """

    for name, index in Resource().resources.items():
        try:
            sm = storage_manager(name)
            count = await sm.storage.count()
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


async def get_alias(name):
    es = ElasticClient.instance()
    return await es.get_alias(name)


async def remove_template(template_name):
    es = ElasticClient.instance()
    if await es.exists_index_template(template_name):
        result = await es.delete_index_template(template_name)
        if not _acknowledged(result):
            return False
    return True


async def add_template(template_name, map) -> Tuple[bool, dict]:
    es = ElasticClient.instance()
    result = await es.put_index_template(template_name, map)
    return _acknowledged(result), result


async def exists_template(template_name) -> bool:
    es = ElasticClient.instance()
    return await es.exists_index_template(template_name)


async def indices(index="*"):
    es = ElasticClient.instance()
    return await es.list_indices(index)


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
    if 'error' in result:
        raise ValueError(f"{result['error']}")
    return _acknowledged(result)


async def remove_index(index: str) -> bool:
    es = ElasticClient.instance()
    if await es.exists_index(index):
        result = await es.remove_index(index)
        if _acknowledged(result):
            return True
    return False


async def get_unique_field_values(index, field, limit=100):
    es = ElasticClient.instance()
    query = {
        "size": 0,
        "aggs": {
            "fields": {
                "terms": {"field": field, "size": limit}
            }
        }}
    index = Resource()[index]
    return StorageRecords.build_from_elastic(await es.search(index.get_index_alias(), query))


async def get_mapping_fields(index: str) -> list:
    db_mappings = await load_fields(index)
    set_of_db_mappings = set(db_mappings)
    set_of_db_mappings.update(FieldMapper().get_field_mapping(index))
    return sorted(list(set_of_db_mappings))
