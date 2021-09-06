from tracardi.exceptions.exception import TracardiException
from tracardi.domain.flow import FlowRecord
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor


async def load_flow(flow_id):
    flow_record_entity = Entity(id=flow_id)
    flow_record = await StorageFor(flow_record_entity).index("flow").load(FlowRecord)  # type: FlowRecord
    if not flow_record:
        raise TracardiException("Could not find flow `{}`".format(flow_id))

    return flow_record.decode()
