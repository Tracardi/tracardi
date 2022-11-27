from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import StorageFor
from typing import List, Tuple, Optional
from tracardi.domain.resource import Resource, ResourceRecord
from tracardi.service.storage.factory import storage_manager, StorageForBulk


async def refresh():
    return await storage_manager('resource').refresh()


async def flush():
    return await storage_manager('resource').flush()


async def load_all(start=0, limit=100) -> StorageRecords:
    return await StorageForBulk().index('resource').load(start, limit)


async def load_destinations(start=0, limit=100) -> Tuple[List[Resource], int]:
    result = await StorageForBulk().index('resource').load(start, limit)
    data = [ResourceRecord.construct(Resource.__fields_set__, **r).decode() for r in result if
            'destination' in r and r['destination'] is not None]
    return data, result.total


async def load_record(id: str) -> Optional[ResourceRecord]:
    return ResourceRecord.create(await storage_manager("resource").load(id))


async def save(data):
    return await storage_manager("resource").upsert(data)


async def save_record(resource: Resource) -> BulkInsertResult:
    resource_record = ResourceRecord.encode(resource)
    return await StorageFor(resource_record).index().save()


async def load_by_tag(tag):
    return await StorageFor.crud('resource', class_type=Resource).load_by('tags', tag)


async def load_by_id(id: str) -> Optional[StorageRecord]:
    return await storage_manager("resource").load(id)


async def load(id: str) -> Resource:
    resource_config_record = await load_record(id)  # type: Optional[ResourceRecord]

    if resource_config_record is None:
        raise ValueError('Resource id {} does not exist.'.format(id))

    if not resource_config_record.enabled:
        raise ValueError('Resource id {} disabled.'.format(id))

    return resource_config_record.decode()


async def delete(id: str):
    sm = storage_manager("resource")
    return await sm.delete(id, index=sm.get_single_storage_index())
