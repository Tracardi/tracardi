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


async def load_event_destinations(event_type, source_id) -> StorageRecords:
    field_value_pairs = [
        ("event_type.id", event_type),
        ("enabled", True),
        ("on_profile_change_only", False),
        ("source.id", source_id)
    ]
    return await storage_manager("destination").load_by_values(field_value_pairs)


async def load_profile_destinations() -> StorageRecords:
    field_value_pairs = [
        ("on_profile_change_only", True)
    ]
    return await storage_manager("destination").load_by_values(field_value_pairs)
