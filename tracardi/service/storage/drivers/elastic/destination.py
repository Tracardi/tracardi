from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.domain.destination import DestinationRecord
from tracardi.domain.entity import Entity
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager, StorageFor


async def load_all(start=0, limit=100, sort=None) -> StorageRecords:
    return await storage_manager("destination").load_all(start, limit, sort)


async def load(id: str) -> DestinationRecord:
    return await StorageFor(Entity(id=id)).index("destination").load(DestinationRecord)


async def save(destination: DestinationRecord) -> BulkInsertResult:
    return await StorageFor(destination).index().save()


async def delete(id: str):
    return await StorageFor(Entity(id=id)).index("destination").delete()


async def refresh():
    return await storage_manager('destination').refresh()
