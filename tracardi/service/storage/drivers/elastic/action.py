from tracardi.service.storage.factory import storage_manager


async def refresh():
    return await storage_manager('action').refresh()


async def flush():
    return await storage_manager('action').flush()
