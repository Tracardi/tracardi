from tracardi.service.storage.factory import storage


async def load_segment_by_event_type(event_type):
    return await storage(index="segment").load_by('eventType', event_type)