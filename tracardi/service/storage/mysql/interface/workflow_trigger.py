from typing import List, Optional, Tuple, Generator

from tracardi.domain.event import Event
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.rule import Rule
from tracardi.service.storage.mysql.mapping.workflow_trigger_mapping import map_to_workflow_trigger_rule

from tracardi.service.storage.mysql.service.workflow_trigger_service import WorkflowTriggerService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

wts = WorkflowTriggerService()


def _records(records: SelectResult, mapper) -> Tuple[List[Rule], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(mapper)), records.count()


async def load_all(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[Rule], int]:
    return _records(await wts.load_all(search, limit, offset), map_to_workflow_trigger_rule)


async def load_by_id(trigger_id: str) -> Optional[Rule]:
    record = await wts.load_by_id(trigger_id)
    if not record.exists():
        return None

    return record.map_to_object(map_to_workflow_trigger_rule)


# Custom

async def load_by_workflow(workflow_id: str, limit: int = None, offset: int = None, ) -> Tuple[List[Rule], int]:
    return _records(await wts.load_by_workflow(workflow_id, limit, offset), map_to_workflow_trigger_rule)


# async def has_rules_for_events(source_id: str, events: List[FlatEvent]) -> bool:
#     # Get event types for valid events
#     event_types = {event.type for event in events if event.is_valid()}
#     return await wts.has_rules_for_events(source_id, event_types)


async def load_by_event_type(event_type_id: str, limit: int = 100) -> Tuple[List[Rule], int]:
    return _records(await wts.load_by_event_type(event_type_id, limit), map_to_workflow_trigger_rule)


# Cache

async def load_rule(event_type_id, source_id) -> List[Rule]:
    records = await wts.load_rule(event_type_id, source_id)
    return list(records.map_to_objects(map_to_workflow_trigger_rule))


async def delete_by_id(trigger_id: str) -> Tuple[bool, Optional[Rule]]:
    return await wts.delete_by_id(trigger_id)


async def delete_by_workflow_id(workflow_id: str) -> str:
    return await wts.delete_by_workflow_id(workflow_id)


async def insert(workflow_trigger: Rule):
    return await wts.insert(workflow_trigger)
