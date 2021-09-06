from tracardi.domain.event import Event
from tracardi.service.storage.factory import StorageFor


async def load_event_by_type(event_type):
    storage = StorageFor.crud('event', class_type=Event).load_by('type', event_type, limit=1)
    return await storage.load_by('type', event_type, limit=1)
