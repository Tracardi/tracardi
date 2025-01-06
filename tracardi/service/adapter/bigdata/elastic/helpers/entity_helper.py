from datetime import datetime

from typing import List, Optional, Tuple

from tracardi.common.time.date import now_in_utc
from tracardi.domain.entity import Entity, NullableEntity
from tracardi.domain.entity_record import EntityRecord, EntityRecordMetadata, EntityRecordTime
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def load(entity_id) -> Optional[EntityRecord]:
    return EntityRecord.create(await storage_manager("entity").load(entity_id))


async def delete_by_id(entity_id: str) -> dict:
    sm = storage_manager("entity")
    return await sm.delete(entity_id, index=sm.get_single_storage_index())


async def _unique_entity_types(bucket_name, buckets_size=500) -> StorageAggregateResult:
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


async def load_entity_types() -> Tuple[List[dict], int]:
    # Returns only 800 types
    result = await _unique_entity_types(bucket_name="type", buckets_size=800)
    return [{
        "id": key,
        "name": key
    } for key, _ in result.aggregations['type'][0].items() if key != "other"], result.total


async def load_integration_id(profile_id: str, system_name: str) -> StorageRecords:
    field_value_pairs = [('type', system_name), ('profile.id', profile_id)]
    return await storage_manager('entity').load_by_values(field_value_pairs)


async def upsert(entity: EntityRecord) -> BulkInsertResult:
    return await storage_manager('entity').upsert(entity)


async def refresh():
    return await storage_manager('entity').refresh()


async def flush():
    return await storage_manager('entity').flush()


async def count(query: dict = None):
    return await storage_manager('entity').count(query)


async def save_integration_id(profile_id: str, system_name: str, remote_id: str,
                              data: Optional[dict] = None) -> BulkInsertResult:
    if data is None:
        data = {}

    record = EntityRecord(
        metadata=EntityRecordMetadata(
            time=EntityRecordTime(
                insert=now_in_utc(),
                update=now_in_utc()
            )
        ),
        id=f"{system_name}:{profile_id}",
        type=system_name,
        profile=Entity(id=profile_id),
        properties=data,
        traits={
            "id": remote_id
        }
    )

    return await upsert(record)


async def upsert_entity(type: str, entity_id: str, referenced_profile_id: str, key: str, properties: dict, traits: dict,
                        due_date: Optional[datetime] = None, expiration_date: Optional[datetime] = None) -> Tuple[BulkInsertResult, EntityRecord]:
    record = EntityRecord(
        metadata=EntityRecordMetadata(
            time=EntityRecordTime(
                insert=now_in_utc(),
                update=now_in_utc(),
                due=due_date,
                expire=expiration_date
            )
        ),
        id=entity_id,
        type=type,
        profile=Entity(id=referenced_profile_id) if referenced_profile_id else NullableEntity(),
        properties={
            key: properties
        },
        traits={
            key: traits
        }
    )

    return await upsert(record), record
