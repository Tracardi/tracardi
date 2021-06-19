from typing import List, Optional

from tracardi_graph_runner.domain.flow import Flow as GraphFlow
import app.service.storage.crud as crud
from .entity import Entity
import app.domain.record as record
from ..exceptions.exception import TracardiException


class Flow(GraphFlow):
    projects: Optional[List[str]] = ["General"]

    # Persistence

    def storage(self) -> crud.StorageCrud:
        return crud.StorageCrud("flow", Flow, entity=self)

    @staticmethod
    async def decode(flow_id) -> 'Flow':
        flow_record_entity = Entity(id=flow_id)
        flow_record = await flow_record_entity.storage("flow").load(record.flow_record.FlowRecord)  # type: FlowRecord

        if not flow_record:
            raise TracardiException("Could not find flow {}".format(flow_id))

        return flow_record.decode()
