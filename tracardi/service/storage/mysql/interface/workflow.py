from typing import Optional, Tuple, List
from tracardi.domain.flow import FlowRecord
from tracardi.service.storage.mysql.map_to_named_entity import map_to_named_entity
from tracardi.service.storage.mysql.mapping.workflow_mapping import map_to_workflow_record
from tracardi.service.storage.mysql.service.workflow_service import WorkflowService
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.worker.domain.named_entity import NamedEntity

ws = WorkflowService()


def _records(records: SelectResult, mapper) -> Tuple[List[FlowRecord], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(mapper)), records.count()


async def _load_all(search: str = None, columns=None, limit: int = None, offset: int = None) -> SelectResult:
    return await ws.load_all(search, limit, offset, columns)


async def _load_by_type(limit, type: str = None, search: str = None):
    if type is None:
        return await ws.load_all(search=search, limit=limit)
    return await ws.load_all_by_type(
        wf_type=type,
        limit=limit,
        search=search
    )


async def load_in_current_context(workflow_id) -> Optional[FlowRecord]:
    record = await ws.load_in_current_context(workflow_id)
    if record is None:
        return None
    return record.map_to_object(map_to_workflow_record)


async def load_named_entities(limit: int, type: Optional[str] = None) -> Tuple[List[NamedEntity], int]:
    records = await _load_by_type(type=type, limit=limit)
    return _records(records, map_to_named_entity)


async def load_flows(type: str, limit: int, search: str = None) -> Tuple[List[FlowRecord], int]:
    records = await _load_by_type(type=type, limit=limit, search=search)
    return _records(records, map_to_workflow_record)


async def load_by_id(workflow_id: str) -> Optional[FlowRecord]:
    record = await ws.load_by_id(workflow_id)
    if record is None:
        return None
    return record.map_to_object(map_to_workflow_record)


# Mutations

async def update_by_id(workflow_id: str, new_data: dict) -> Optional[str]:
    return await ws.update_by_id(workflow_id, new_data=new_data)


async def delete_by_id(workflow_id: str) -> Tuple[bool, Optional[FlowRecord]]:
    return await ws.delete_by_id(workflow_id)


async def insert(workflow: FlowRecord):
    return await ws.insert(workflow)
