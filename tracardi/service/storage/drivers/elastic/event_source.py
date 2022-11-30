from typing import Tuple, List, Optional
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.event_source import EventSource
from tracardi.service.storage.factory import storage_manager


async def refresh():
    return await storage_manager('event-source').refresh()


async def flush():
    return await storage_manager('event-source').flush()


async def load(id: str) -> Optional[EventSource]:
    return EventSource.create(await storage_manager("event-source").load(id))


async def load_all(limit=100):
    return await storage_manager('event-source').load_all(limit=limit)


async def load_by_tag(tag):
    return await storage_manager('event-source').load_by('tags', tag)


async def load_by(field, value):
    return await storage_manager('event-source').load_by(field, value)


async def delete_by_id(id: str):
    sm = storage_manager('event-source')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def save(event_source: EventSource) -> BulkInsertResult:
    return await storage_manager('event-source').upsert(event_source)
