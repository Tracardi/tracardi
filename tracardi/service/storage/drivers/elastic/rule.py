import asyncio
import logging
from asyncio import Task
from typing import List, Tuple, Dict

from tracardi.config import tracardi
from tracardi.domain.entity import Entity
from tracardi.domain.storage_result import StorageResult

from tracardi.domain.rule import Rule

from tracardi.domain.event import Event
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.factory import storage_manager

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

memory_cache = MemoryCache()


def _get_cache_key(source_id, event_type):
    return f"rules-{source_id}-{event_type}"


async def _load_rule(event_type, source_id):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "event.type": event_type.strip()
                        }
                    },
                    {
                        "term": {
                            "source.id": source_id
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
    return await storage_manager(index="rule").filter(query)


async def _get_rules_for_source_and_event_type(source: Entity, events: List[Event]) -> Dict[str, List[Dict]]:
    event_types = {event.type for event in events}

    # Cache rules per event types

    event_type_rules = {}

    for event_type in event_types:

        cache_key = _get_cache_key(source.id, event_type)
        if cache_key not in memory_cache:
            logger.debug("Loading routing rules for cache key {}".format(cache_key))
            rules = await _load_rule(event_type, source.id)

            # todo set MemoryCache ttl from env
            memory_cache[cache_key] = CacheItem(data=rules, ttl=15)

        event_type_rules[event_type] = list(memory_cache[cache_key].data)

    return event_type_rules


def _read_rule(event_type: str, rules: Dict[str, List[Dict]]) -> List[Dict]:
    if event_type not in rules:
        return []

    return rules[event_type]


async def load_rules(source: Entity, events: List[Event]) -> List[Tuple[List[Dict], Event]]:
    rules = await _get_rules_for_source_and_event_type(source, events)

    return [(_read_rule(event.type, rules), event) for event in events]


async def load_flow_rules(flow_id: str) -> List[Rule]:
    rules_attached_to_flow = await storage_manager('rule').load_by('flow.id', flow_id)
    return [Rule(**rule) for rule in rules_attached_to_flow]


async def load_all(start: int = 0, limit: int = 100) -> StorageResult:
    return await storage_manager('rule').load_all(start, limit=limit)


async def refresh():
    return await storage_manager('rule').refresh()


async def flush():
    return await storage_manager('rule').flush()
