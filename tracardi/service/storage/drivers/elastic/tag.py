import logging
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.config import memory_cache as memory_cache_config, tracardi
from tracardi.service.storage.factory import storage_manager
from typing import List
from tracardi.domain.event_tag import EventTag

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
memory_cache = MemoryCache()


async def refresh_tags_cache_for_type(event_type: str):
    key = "tags-type-{}".format(event_type)
    logger.info("Refreshing memory cache for {}".format(key))
    records = list(await get_by_type(event_type))
    if len(records) > 1:
        raise ValueError("There is more then 1 record in tags index for event type {}. ".format(event_type))
    if records and len(records) > 0:
        result = records.pop()  # There is only one record
        cache_data = EventTag(**result).tags
    else:
        cache_data = []
    logger.info("Refreshed value for {} is {}".format(key, cache_data))
    memory_cache[key] = CacheItem(
        data=cache_data,
        ttl=memory_cache_config.tags_ttl
    )


async def get_tags(event_type) -> list:
    key = "tags-type-{}".format(event_type)
    if key not in memory_cache:
        await refresh_tags_cache_for_type(event_type)

    return memory_cache[key].data


async def get_by_type(event_type):
    return await storage_manager("event-tags").load_by(field="type", value=event_type)


async def replace(event_type: str, tags: List[str]):
    return await storage_manager("event-tags").upsert({
        "_id": event_type,
        "type": event_type,
        "tags": tags
    })


async def refresh():
    return await storage_manager("event-tags").refresh()


async def flush():
    return await storage_manager("event-tags").flush()


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


async def load_tags(limit: int = 100, query_string: str = ""):
    if not query_string:
        return (await storage_manager("event-tags").load_all(start=0, limit=limit)).dict()["result"]
    else:
        query = {
            "from": 0,
            "size": limit,
            "query": {
                "wildcard": {
                    "type": f"{query_string}*"
                }
            }
        }

        result = await storage_manager("event-tags").query(query)
        return result


async def delete(event_type: str):
    return await storage_manager("event-tags").delete(event_type)
