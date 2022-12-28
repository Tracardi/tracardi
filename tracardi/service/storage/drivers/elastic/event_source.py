import logging
from typing import Tuple, List, Optional

from tracardi.config import tracardi
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.factory import storage_manager

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def refresh():
    return await storage_manager('event-source').refresh()


async def flush():
    return await storage_manager('event-source').flush()


async def load(id: str) -> Optional[EventSource]:
    return EventSource.create(await storage_manager("event-source").load(id))


async def load_by_active_event_sources_bridge_id(bridge_id: str) -> List[EventSource]:
    result = await storage_manager("event-source").load_by_values(
        [("bridge.id", bridge_id), ("enabled", True)]
    )
    return result.to_domain_objects(EventSource)


async def load_all(limit=100):
    return await storage_manager('event-source').load_all(limit=limit)


async def load_by_tag(tag):
    return await storage_manager('event-source').load_by('tags', tag)


async def load_by_bridge(bridge_id):
    return await storage_manager('event-source').load_by('bridge.id', bridge_id)


async def load_by(field, value):
    return await storage_manager('event-source').load_by(field, value)


async def delete_by_id(id: str):
    sm = storage_manager('event-source')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def save(event_source: EventSource) -> BulkInsertResult:
    return await storage_manager('event-source').upsert(event_source)


async def unlock_event_source_by_bridge(bridge_id):
    event_source_records = await load_by_bridge(bridge_id)
    for event_source_record in event_source_records:
        locked = event_source_record.get('locked', False)
        if locked:
            event_source = event_source_record.to_entity(EventSource)
            event_source.locked = False
            lock_result = await save(event_source)
            logger.info(f"Event source `{event_source.name}` unlocked with result {lock_result}")
