from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.exceptions.exception import TracardiException
from tracardi.domain.flow import FlowRecord
from tracardi.service.storage.factory import storage_manager
from tracardi.service.storage.mysql.mapping.workflow_mapping import map_to_workflow_record
from tracardi.service.storage.mysql.service.workflow_service import WorkflowService


# async def load_record(id: str) -> Optional[FlowRecord]:
#     return FlowRecord.create(await storage_manager("flow").load(id))


# async def save_record(flow_record: FlowRecord) -> BulkInsertResult:
#     return await storage_manager("flow").upsert(flow_record)


# async def save(flow: NamedEntity) -> BulkInsertResult:
#     return await storage_manager("flow").upsert(flow)


# async def load_production_flow(flow_id):
#     ws = WorkflowService()
#
#     flow_record = (await ws.load_by_id(flow_id)).map_to_object(map_to_workflow_record)
#     if not flow_record:
#         raise TracardiException("Could not find flow `{}`".format(flow_id))
#
#     return flow_record.get_production_workflow()


# async def load_draft_flow(flow_id):
#     flow_record = await load_record(flow_id)
#     if not flow_record:
#         raise TracardiException("Could not find flow `{}`".format(flow_id))
#
#     return flow_record.get_draft_workflow()


# async def load_all(start: int = 0, limit: int = 100):
#     return await storage_manager('flow').load_all(start=start, limit=limit)


# async def filter(type: str, limit: int = 100):
#     query = {
#         "size": limit,
#         "query": {
#             "term": {
#                 "type": type
#             }
#         }
#     }
#     return await storage_manager('flow').query(query)


# async def refresh():
#     return await storage_manager('flow').refresh()


# async def flush():
#     return await storage_manager('flow').flush()


# async def delete_by_id(id: str):
#     sm = storage_manager("flow")
#     return await sm.delete(id, index=sm.get_single_storage_index())


# async def load_by_id(id: str):
#     return await storage_manager("flow").load(id)