from typing import Tuple, List

from tracardi.domain.event_redirect import EventRedirect
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, StorageForBulk
from tracardi.service.storage.factory import storage_manager


async def refresh():
    return await storage_manager('event-redirect').refresh()


async def flush():
    return await storage_manager('event-redirect').flush()


async def load_by_id(id: str) -> EventRedirect:
    # TODO add caching
    return await StorageFor(Entity(id=id)).index("event-redirect").load(EventRedirect)  # type: EventRedirect


async def load_all(limit=100) -> Tuple[List[EventRedirect], int]:
    result = await StorageForBulk().index('event-redirect').load(limit=limit)
    data = [EventRedirect(**r) for r in result]
    return data, result.total


async def delete_by_id(id: str):
    return await StorageFor(Entity(id=id)).index("event-redirect").delete()


async def save(event_redirect: EventRedirect) -> BulkInsertResult:
    # TODO add caching
    return await StorageFor(event_redirect).index().save()
