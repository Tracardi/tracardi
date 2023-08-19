from typing import Optional

from tracardi.domain.storage_record import StorageRecord
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_type_metadata import EventTypeMetadata


async def save(event_type_metadata: EventTypeMetadata):
    return await storage_manager("event-management").upsert(event_type_metadata)


async def del_event_type_mapping(event_type: str):
    sm = storage_manager("event-management")
    return await sm.delete(event_type, index=sm.get_single_storage_index())


async def get_event_type_mapping(event_type: str) -> Optional[StorageRecord]:
    return await storage_manager("event-management").load(event_type)


async def load_events_type_mapping(start: int = 0, limit: int = 10):
    return await storage_manager("event-management").load_all(start, limit)


async def refresh():
    return await storage_manager('event-management').refresh()


async def flush():
    return await storage_manager('event-management').flush()
