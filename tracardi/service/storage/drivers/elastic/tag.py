from tracardi.service.storage.factory import storage_manager
from typing import List
from tracardi.domain.event_tag import EventTag


async def get_by_type(event_type):
    return await storage_manager("event-tags").load_by(field="type", value=event_type)


async def add(event_type: str, tags: List[str]):
    search_result = await get_by_type(event_type=event_type)
    storage = storage_manager("event-tags")
    if search_result.total == 1:
        record = list(search_result).pop()
        tag = EventTag(**record)
        tag.tags.extend(tags)
        tag.tags = list(set(tag.tags))
        return await storage.upsert({
            "_id": event_type,
            "type": event_type,
            "tags": tag.tags
        })
    else:
        return await storage.upsert({
            "_id": event_type,
            "type": event_type,
            "tags": tags
        })


async def remove(event_type: str, tags: List[str]):
    search_result = await get_by_type(event_type=event_type)
    if search_result.total == 1:
        record = list(search_result).pop()
        tag = EventTag(**record)
        old_tags_number = len(tag.tags)
        tag.tags = list(set(tag.tags).difference(set(tags)))
        storage = storage_manager("event-tags")
        if tag.tags:
            result = await storage.upsert({
                "_id": event_type,
                "type": event_type,
                "tags": tag.tags
            })
        else:
            result = await storage.delete(event_type)
        return len(tag.tags), old_tags_number - len(tag.tags), result
    else:
        raise ValueError("There is no document with 'type' field equal to '{}'.".format(event_type))


async def load_tags(limit: int = 100):
    return await storage_manager("event-tags").load_all(start=0, limit=limit)
