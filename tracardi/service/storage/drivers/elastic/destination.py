from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.domain.destination import DestinationRecord
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager


async def load_all(start=0, limit=100, sort=None) -> StorageRecords:
    return await storage_manager("destination").load_all(start, limit, sort)


async def load(id: str) -> DestinationRecord:
    return DestinationRecord.create(await storage_manager("destination").load(id))


async def save(destination: DestinationRecord) -> BulkInsertResult:
    return await storage_manager("destination").upsert(destination)


async def delete(id: str):
    sm = storage_manager('destination')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def refresh():
    return await storage_manager('destination').refresh()
