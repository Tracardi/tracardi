from typing import Optional
from .flow_graph_data import FlowGraphData
from .flow_response import FlowResponse
from .named_entity import NamedEntity


class Flow(NamedEntity):
    description: Optional[str] = None
    flowGraph: Optional[FlowGraphData] = None
    response: Optional[FlowResponse] = FlowResponse()
