import asyncio
from asyncio import Task
from typing import List, Tuple

from tracardi.domain.storage_result import StorageResult

from tracardi.domain.rule import Rule

from tracardi.domain.event import Event
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.service.storage.factory import storage_manager


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
                            "event.type": event_type
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
        flows_data = await storage_manager(index="rule").filter(query)
        memory_cache['rules'] = CacheItem(data=flows_data, ttl=1)

    rules = list(memory_cache['rules'].data)

    return rules


async def load_flow_rules(flow_id: str) -> List[Rule]:
    rules_attached_to_flow = await storage_manager('rule').load_by('flow.id', flow_id)
    return [Rule(**rule) for rule in rules_attached_to_flow]


async def load_all(start: int = 0, limit: int = 100) -> StorageResult:
    return await storage_manager('rule').load_all(start, limit=limit)


async def refresh():
    return await storage_manager('rule').refresh()


async def flush():
    return await storage_manager('rule').flush()
