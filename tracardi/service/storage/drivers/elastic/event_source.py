from typing import Tuple, List

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.domain.entity import Entity
from tracardi.domain.event_source import EventSource
from tracardi.service.storage.factory import StorageFor, StorageForBulk
from tracardi.service.storage.factory import storage_manager


async def refresh():
    return await storage_manager('event-source').refresh()


async def flush():
    return await storage_manager('event-source').flush()


async def load(id: str) -> EventSource:
    return await StorageFor(Entity(id=id)).index("event-source").load(EventSource)


async def load_all(limit=100) -> Tuple[List[EventSource], int]:
    result = await StorageForBulk().index('event-source').load(limit=limit)
    data = [EventSource(**r) for r in result]
    return data, result.total


async def load_by_tag(tag):
    return await StorageFor.crud('event-source', class_type=EventSource).load_by('tags', tag)


async def delete(id: str):
    return await StorageFor(Entity(id=id)).index("event-source").delete()


async def save(event_source: EventSource) -> BulkInsertResult:
    return await StorageFor(event_source).index().save()
