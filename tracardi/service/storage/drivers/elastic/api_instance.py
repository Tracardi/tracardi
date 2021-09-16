from tracardi.service.storage.factory import storage_manager


async def load_all():
    return await storage_manager('api-instance').load_all()
