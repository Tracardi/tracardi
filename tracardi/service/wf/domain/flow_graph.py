from typing import Optional, Any, Dict, List
from .flow_graph_data import FlowGraphData
from .flow_response import FlowResponse
from .named_entity import NamedEntity
from pydantic import PrivateAttr

from ...change_monitoring.field_change_monitor import FieldChangeTimestampManager


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
        self._change_monitor = FieldChangeTimestampManager()

    def set_change(self, type, profile_id, event_id, session_id, source_id, key, value, old_value):
        self._change_monitor.append(type, profile_id, event_id, session_id, source_id, key, value, old_value)

    def get_changes(self) -> List[dict]:
        return self._change_monitor.get_list()