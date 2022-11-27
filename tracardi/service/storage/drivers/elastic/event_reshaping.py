from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from typing import Optional


async def refresh():
    return await storage_manager('event-reshaping').refresh()


async def flush():
    return await storage_manager('event-reshaping').flush()


async def upsert(data: EventReshapingSchema):
    return await storage_manager('event-reshaping').upsert(data, replace_id=True)


async def load_by_id(id: str) -> Optional[EventReshapingSchema]:
    return EventReshapingSchema.create(await storage_manager("event-reshaping").load(id))


async def load_all(limit=100) -> StorageRecords:
    return await storage_manager('event-reshaping').load_all(limit=limit)


async def load_by_tag(tag) -> StorageRecords:
    return await storage_manager('event-reshaping').load_by('tags', tag)


async def load_by_event_type(event_type: str) -> StorageRecords:
    return await storage_manager('event-reshaping').load_by_values(
        [('event_type', event_type), ('enabled', True)]
    )


async def delete(id: str):
    sm = storage_manager("event-reshaping")
    return await sm.delete(id, index=sm.get_single_storage_index())


async def count_by_type(event_type: str) -> int:
    return await storage_manager("event-reshaping").count({"query": {"term": {"event_type": event_type}}})
