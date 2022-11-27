from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.event_validator import EventValidator
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, StorageForBulk
from typing import Optional


async def refresh():
    return await storage_manager('event-validation').refresh()


async def flush():
    return await storage_manager('event-validation').flush()


async def upsert(validator: EventValidator):
    return await storage_manager("event-validation").upsert(validator, replace_id=True)


async def load(id: str) -> Optional[EventValidator]:
    result: EventValidator = await StorageFor(Entity(id=id)).index("event-validation").load(
        EventValidator
    )
    return result


async def load_all(limit=100) -> StorageRecords:
    return await StorageForBulk().index('event-validation').load(limit=limit)


async def load_by_tag(tag):
    return await StorageFor.crud('event-validation', class_type=EventValidator).load_by('tags', tag)


async def load_by_event_type(event_type: str) -> StorageRecords:
    return await StorageFor.crud('event-validation', class_type=EventValidator).load_by_values(
        [('event_type', event_type), ('enabled', True)]
    )


async def delete(id: str):
    sm = storage_manager("event-validation")
    return sm.delete(id, index=sm.get_single_storage_index())


async def count_by_type(event_type: str) -> int:
    return await storage_manager("event-validation").count({"query": {"term": {"event_type": event_type}}})
