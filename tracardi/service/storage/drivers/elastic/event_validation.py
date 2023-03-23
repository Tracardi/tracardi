from tracardi.domain.entity import Entity
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_validator import EventValidator
from typing import Optional


async def refresh():
    return await storage_manager('event-validation').refresh()


async def flush():
    return await storage_manager('event-validation').flush()


async def upsert(validator: Entity):
    return await storage_manager("event-validation").upsert(validator, replace_id=True)


async def load(id: str) -> Optional[EventValidator]:
    result = EventValidator.create(await storage_manager("event-validation").load(id))
    return result


async def load_all(limit=100) -> StorageRecords:
    return await storage_manager('event-validation').load_all(limit=limit)


async def load_by_tag(tag):
    return await storage_manager('event-validation').load_by('tags', tag)


async def load_by_event_type(event_type: str, only_enabled: bool = True) -> StorageRecords:
    if only_enabled is True:
        query = [('event_type', event_type), ('enabled', True)]
    else:
        query = [('event_type', event_type)]
    return await storage_manager('event-validation').load_by_values(query)


async def delete(id: str):
    sm = storage_manager("event-validation")
    return await sm.delete(id, index=sm.get_single_storage_index())


async def count_by_type(event_type: str) -> int:
    return await storage_manager("event-validation").count({"query": {"term": {"event_type": event_type}}})
