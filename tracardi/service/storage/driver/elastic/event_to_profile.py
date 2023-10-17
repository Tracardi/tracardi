from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import storage_manager


async def save(event_to_profile: EventToProfile) -> BulkInsertResult:
    return await storage_manager("event-to-profile").upsert(event_to_profile)


async def del_event_type_metadata(event_type: str):
    sm = storage_manager("event-to-profile")
    return await sm.delete(event_type, index=sm.get_single_storage_index())


async def load_by_id(event_id: str):
    sm = storage_manager("event-to-profile")
    return await sm.load(event_id)


async def get_event_to_profile(event_type: str, enabled_only: bool = False) -> StorageRecords:
    fields = [("event_type.id", event_type)]
    if enabled_only:
        fields.append(("enabled", True))
    return await storage_manager("event-to-profile").load_by_values(fields)


async def load_events_to_profiles(start: int = 0, limit: int = 200) -> StorageRecords:
    return await storage_manager("event-to-profile").load_all(start, limit)


async def refresh():
    return await storage_manager('event-to-profile').refresh()


async def flush():
    return await storage_manager('event-to-profile').flush()
