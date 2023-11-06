from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import storage_manager


async def upsert(entity) -> BulkInsertResult:
    return await storage_manager('dispatch-log').upsert(entity)


async def refresh():
    return await storage_manager('dispatch-log').refresh()


async def flush():
    return await storage_manager('dispatch-log').flush()

