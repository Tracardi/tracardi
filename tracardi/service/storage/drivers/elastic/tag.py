from tracardi.service.storage.factory import storage_manager
from typing import List


async def get_document_by_event_type(event_type):
    return await storage_manager("event-tags").load_by(field="type", value=event_type)


async def add_tags(event_type: str, tags: List[str]):
    search_result = await get_document_by_event_type(event_type=event_type)
    if search_result.dict()["result"]:
        tags.extend(search_result.dict()["result"][0]["tags"])
        tags = list(set(tags))
        return 1, await storage_manager("event-tags").upsert({
            "_id": search_result.dict()["result"][0]["id"],
            "type": search_result.dict()["result"][0]["type"],
            "tags": tags
        })
    else:
        return 0, await storage_manager("event-tags").upsert({
            "type": event_type,
            "tags": tags
        })


async def remove_tags(event_type: str, tags: List[str]):
    search_result = await get_document_by_event_type(event_type=event_type)
    if search_result.dict()['result']:
        if set(tags).issubset(set(search_result.dict()["result"][0]["tags"])):
            return 0, \
                   len(search_result.dict()["result"][0]["tags"]), \
                   await storage_manager("event-tags").delete_by(field="type", value=event_type)
        else:
            tags_to_insert = [tag for tag in search_result.dict()["result"][0]["tags"] if tag not in tags]
            return len(tags_to_insert), \
                len(search_result.dict()["result"][0]["tags"]) - len(tags_to_insert), \
                await storage_manager("event-tags").upsert({
                    "_id": search_result.dict()["result"][0]["id"],
                    "type": event_type,
                    "tags": tags_to_insert
                })
    else:
        raise ValueError("There is no document with 'type' field equal to '{}'.".format(event_type))


async def load_all_tags(limit):
    return storage_manager("event-tags").load_all(start=0, limit=limit)
