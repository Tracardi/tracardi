from tracardi.service.storage.factory import storage_manager


async def load_segment_by_event_type(event_type):
    return await storage_manager(index="segment").load_by('eventType', event_type)
