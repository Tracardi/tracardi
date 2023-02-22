import asyncio
import logging
from asyncio import Task
from typing import List, Tuple, Dict, Optional

from tracardi.config import tracardi
from tracardi.domain.entity import Entity
from tracardi.domain.storage_record import StorageRecords

from tracardi.domain.rule import Rule

from tracardi.domain.event import Event
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.event_server.utils.memory_cache import MemoryCache, CacheItem
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.factory import storage_manager

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

memory_cache = MemoryCache("rules")


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


async def _get_rules_for_source_and_event_type(source: Entity, events: List[Event]) -> Tuple[
    Dict[str, List[Dict]], bool]:
    event_types = {event.type for event in events}

    # Cache rules per event types

    event_type_rules = {}
    has_routes = False
    for event_type in event_types:

        cache_key = _get_cache_key(source.id, event_type)
        if cache_key not in memory_cache:
            logger.debug("Loading routing rules for cache key {}".format(cache_key))
            rules = await _load_rule(event_type, source.id)

            # todo set MemoryCache ttl from env
            memory_cache[cache_key] = CacheItem(data=rules, ttl=15)

        routes = list(memory_cache[cache_key].data)
        if not has_routes and routes:
            has_routes = True

        event_type_rules[event_type] = routes

    return event_type_rules, has_routes


def _read_rule(event_type: str, rules: Dict[str, List[Dict]]) -> List[Dict]:
    if event_type not in rules:
        return []

    return rules[event_type]


async def load_rules(source: Entity, events: List[Event]) -> Optional[List[Tuple[List[Dict], Event]]]:
    rules, has_routing_rules = await _get_rules_for_source_and_event_type(source, events)

    if not has_routing_rules:
        return None

    return [(_read_rule(event.type, rules), event) for event in events]


async def load_flow_rules(flow_id: str) -> List[Rule]:
    rules_attached_to_flow = await storage_manager('rule').load_by('flow.id', flow_id)
    return [Rule(**rule) for rule in rules_attached_to_flow]


async def load_all(start: int = 0, limit: int = 100) -> StorageRecords:
    return await storage_manager('rule').load_all(start, limit=limit)


async def load_by_id(id) -> Optional[Rule]:
    return Rule.create(await storage_manager("rule").load(id))


async def delete_by_id(id) -> dict:
    sm = storage_manager('rule')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def save(rule: Rule) -> BulkInsertResult:
    return await storage_manager('rule').upsert(rule)


async def refresh():
    return await storage_manager('rule').refresh()


async def flush():
    return await storage_manager('rule').flush()


async def load_by_event_type(max_group: int = 20) -> StorageRecords:
    query = {
        "query": {"match_all": {}},
        "collapse": {
            "field": "event.type",
            "inner_hits": {
                "name": "types",
                "size": max_group
            }
        }
    }
    return await storage_manager('rule').query(query)
