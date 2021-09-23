from tracardi.service.storage.factory import storage_manager


async def load_all(start: int = 0, limit: int = 100):
    return await storage_manager('api-instance').load_all(start, limit)
