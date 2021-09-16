from tracardi.service.storage.factory import storage_manager


async def load_segment_by_event_type(event_type):
    return await storage_manager(index="segment").load_by('eventType', event_type)


async def refresh():
    return await storage_manager('segment').refresh()


async def flush():
    return await storage_manager('segment').flush()
