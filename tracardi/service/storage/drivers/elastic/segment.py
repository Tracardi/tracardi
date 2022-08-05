from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.factory import storage_manager


async def load_segments(event_type, limit=500) -> StorageResult:
    return await storage_manager(index="segment").\
        load_by_query_string("(NOT _exists_:eventType) OR eventType: \"{}\"".format(event_type, limit))


async def refresh():
    return await storage_manager('segment').refresh()


async def flush():
    return await storage_manager('segment').flush()


async def save(data: dict):
    return await storage_manager('segment').upsert(data)
