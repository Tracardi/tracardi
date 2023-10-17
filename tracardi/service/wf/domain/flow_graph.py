from typing import Optional, Any, Dict
from .flow_graph_data import FlowGraphData
from .flow_response import FlowResponse
from .named_entity import NamedEntity
from pydantic import ConfigDict


class FlowGraph(NamedEntity):
    description: Optional[str] = None
    flowGraph: Optional[FlowGraphData] = None
    # response: Optional[FlowResponse] = FlowResponse()
    response: Optional[Dict[str, dict]] = {}

    # model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: Any):
        if 'response' in data and isinstance(data['response'], dict):
            data['response'] = FlowResponse(data['response'])
        super().__init__(**data)
