from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult

from tracardi.exceptions.exception import TracardiException
from tracardi.domain.flow import FlowRecord
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, storage_manager


async def load_record(flow_id) -> FlowRecord:
    flow_record_entity = Entity(id=flow_id)
    return await StorageFor(flow_record_entity).index("flow").load(FlowRecord)  # type: FlowRecord


async def save_record(flow_record: FlowRecord) -> BulkInsertResult:
    return await StorageFor(flow_record).index().save()


async def load_production_flow(flow_id):
    flow_record = await load_record(flow_id)
    if not flow_record:
        raise TracardiException("Could not find flow `{}`".format(flow_id))

    return flow_record.get_production_workflow()


async def load_draft_flow(flow_id):
    flow_record = await load_record(flow_id)
    if not flow_record:
        raise TracardiException("Could not find flow `{}`".format(flow_id))

    return flow_record.get_draft_workflow()


async def refresh():
    return await storage_manager('flow').refresh()


async def flush():
    return await storage_manager('flow').flush()
