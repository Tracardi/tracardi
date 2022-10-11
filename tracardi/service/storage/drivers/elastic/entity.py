from typing import List

from tracardi.domain.entity_record import EntityRecord
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, storage_manager


async def load_by_id(entity_id) -> EntityRecord:
    entity = Entity(id=entity_id)
    return await StorageFor(entity).index("entity").load(EntityRecord)  # type: EntityRecord


async def load_by_values(field_value_pairs: List[tuple]) -> StorageRecords:
    return await storage_manager('entity').load_by_values(field_value_pairs)


async def delete_by_id(entity_id) -> dict:
    entity = Entity(id=entity_id)
    return await StorageFor(entity).index("entity").delete()


async def unique_entity_types(bucket_name, buckets_size=500) -> StorageAggregateResult:
    async def _aggregate(bucket_name, by, filter_query=None, buckets_size=15) -> StorageAggregateResult:
        aggregate_query = {
            bucket_name: {
                "terms": {
                    "field": by,
                    "size": buckets_size,
                }
            }
        }

        if filter_query is None:
            filter_query = {
                "match_all": {}
            }

        query = {
            "size": 0,
            "query": filter_query,
            "aggs": aggregate_query
        }

        return await storage_manager(index="entity").aggregate(query)

    return await _aggregate(bucket_name, "type", buckets_size=buckets_size)


async def upsert(entity: EntityRecord) -> BulkInsertResult:
    return await StorageFor(entity).index().save()


async def refresh():
    return await storage_manager('entity').refresh()


async def flush():
    return await storage_manager('entity').flush()
