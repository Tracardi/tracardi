from typing import Optional

from tracardi.domain.event_redirect import EventRedirect
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import storage_manager


async def refresh():
    return await storage_manager('event-redirect').refresh()


async def flush():
    return await storage_manager('event-redirect').flush()


async def load_by_id(id: str) -> Optional[EventRedirect]:
    # TODO add caching
    return EventRedirect.create(await storage_manager("event-redirect").load(id))


async def load_all(start=0, limit=100) -> StorageRecords:
    return await storage_manager('event-redirect').load_all(start, limit=limit)


async def delete_by_id(id: str):
    sm = storage_manager('event-redirect')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def save(event_redirect: EventRedirect) -> BulkInsertResult:
    # TODO add caching
    return await storage_manager('event-redirect').upsert(event_redirect)
