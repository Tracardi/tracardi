from typing import List, Optional, Tuple

from tracardi.domain.event import Event
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.rule import Rule
from tracardi.service.cache.cache_tags import WORKFLOW_TRIGGER_TAG
from tracardi.service.cache_change_tagger.change_tagger import invalidate_cache_on_update
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


async def load_rule(event_type_id, source_id):
    return await wts.load_rule(event_type_id, source_id)


async def has_rules_for_events(source_id: str, events: List[FlatEvent]) -> bool:
    return await wts.has_rules_for_events(source_id, events)


async def load_by_source_and_events(source_id: str, events: List[Event]) -> Optional[
    List[Tuple[List[Rule], Event]]]:
    return await wts.load_by_source_and_events(source_id, events)


async def load_by_event_type(event_type_id: str, limit: int = 100) -> Tuple[List[Rule], int]:
    return _records(await wts.load_by_event_type(event_type_id, limit), map_to_workflow_trigger_rule)


# async def load_by_segment(segment_id: str, limit: int = 100) -> SelectResult:
#     return await wts.load_by_segment(segment_id, limit)


# Mutations

async def delete_by_id(trigger_id: str) -> Tuple[bool, Optional[Rule]]:
    with invalidate_cache_on_update(*WORKFLOW_TRIGGER_TAG):
        return await wts.delete_by_id(trigger_id)


async def delete_by_workflow_id(workflow_id: str) -> str:
    with invalidate_cache_on_update(*WORKFLOW_TRIGGER_TAG):
        return await wts.delete_by_workflow_id(workflow_id)


async def insert(workflow_trigger: Rule):
    with invalidate_cache_on_update(*WORKFLOW_TRIGGER_TAG):
        return await wts.insert(workflow_trigger)
