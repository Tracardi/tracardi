from typing import Optional
from .flow_graph_data import FlowGraphData
from .flow_response import FlowResponse
from .named_entity import NamedEntity
from pydantic import ConfigDict


class FlowGraph(NamedEntity):
    description: Optional[str] = None
    flowGraph: Optional[FlowGraphData] = None
    response: Optional[FlowResponse] = FlowResponse()

    model_config = ConfigDict(arbitrary_types_allowed=True)
