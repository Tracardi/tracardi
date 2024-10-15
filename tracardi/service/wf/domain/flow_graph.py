from typing import Optional, Any, Dict
from .flow_graph_data import FlowGraphData
from .flow_response import FlowResponse
from .named_entity import NamedEntity
from pydantic import PrivateAttr

from ...change_monitoring.field_change_logger import FieldChangeLogger


class FlowGraph(NamedEntity):
    description: Optional[str] = None
    flowGraph: Optional[FlowGraphData] = None
    response: Optional[Dict[str, dict]] = {}

    _updated_in_workflow: dict = PrivateAttr({})

    def __init__(self, **data: Any):
        if 'response' in data and isinstance(data['response'], dict):
            data['response'] = FlowResponse(data['response'])
        super().__init__(**data)
        # This is local fields timestamp monitor per one WF.
        # It is merged with other top WorkflowAsyncManager to get global status of changed fields.
        self._field_change_logger = FieldChangeLogger()

    def set_change(self, key, old_value):
        self._field_change_logger.log(key, old_value)

    def get_change_log(self) -> FieldChangeLogger:
        return self._field_change_logger