import asyncio
from asyncio import Task
from typing import List, Tuple

from tracardi.domain.event import Event
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.service.storage.factory import storage


def load_rules(events: List[Event]) -> List[Tuple[Task, Event]]:
    return [(
        asyncio.create_task(load_rule(event.type)),
        event
    ) for event in events]


async def load_rule(event_type: str):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "event.type.keyword": event_type
                        }
                    },
                    {
                        "match": {
                            "enabled": True
                        }
                    }
                ]
            }
        }
    }

    # todo set MemoryCache ttl from env
    memory_cache = MemoryCache()

    if 'rules' not in memory_cache:
        flows_data = await storage(index="rule").filter(query)
        memory_cache['rules'] = CacheItem(data=flows_data, ttl=1)

    rules = list(memory_cache['rules'].data)

    return rules
