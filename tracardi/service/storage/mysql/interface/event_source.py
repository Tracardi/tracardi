from typing import List, Tuple, Optional, Dict

from tracardi.domain.event_source import EventSource
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source
from tracardi.service.storage.mysql.service.event_source_service import EventSourceService

ess = EventSourceService()


def _records(records) -> Tuple[List[EventSource], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_event_source)), records.count()


async def lock_event_source_by_id(service_id, lock: bool):
    await ess.lock_by_bridge_id(service_id, lock=lock)


async def load_active_event_sources_by_bridge_id(bridge_id: str) -> Tuple[List[EventSource], int]:
    records = await ess.load_active_by_bridge_id(bridge_id)
    return _records(records)


async def load_event_source_by_id(source_id) -> Optional[EventSource]:
    record = await ess.load_by_id_in_deployment_mode(source_id)

    if not record.exists():
        return None

    return record.map_to_object(map_to_event_source)


async def load_all_event_sources(query, limit) -> Tuple[List[EventSource], int]:
    records = await ess.load_all_in_deployment_mode(query, limit=limit)
    return _records(records)


def load_event_source_types(type: str) -> Tuple[List[Dict], int]:
    types = ess.event_source_types()

    if type == 'name':
        types = {id: item['name'] for id, item in types.items()}

    return types, len(types)


async def load_event_source_entities(add_current: bool = False, type: Optional[str] = None) -> Tuple[
    List[NamedEntity], int]:
    if type:
        records = await ess.load_by_type_in_deployment_mode(type)
    else:
        records = await ess.load_all_in_deployment_mode()

    if not records.exists():
        return [], 0

    total = records.count()
    result = records.as_named_entities(rewriter=lambda r: f"{r.name} ({r.type})")

    if add_current is True:
        total += 1
        result.append(NamedEntity(id="@current-source", name="@current-source"))

    return result, total


async def delete_event_source(source_id: str):
    await ess.delete_by_id_in_deployment_mode(source_id)


async def insert_event_source(event_source: EventSource):
    return await ess.save(event_source)
