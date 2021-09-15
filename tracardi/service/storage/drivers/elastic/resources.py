from typing import List, Tuple

from tracardi.domain.resource import Resource, ResourceRecord

from tracardi.service.storage.factory import storage_manager, StorageForBulk


async def refresh():
    return await storage_manager('resource').refresh()


async def flush():
    return await storage_manager('resource').flush()


async def load_all() -> Tuple[List[Resource], int]:
    result = await StorageForBulk().index('resource').load()
    data = [ResourceRecord.construct(Resource.__fields_set__, **r).decode() for r in result]
    return data, result.total
