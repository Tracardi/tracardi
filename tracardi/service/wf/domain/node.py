from typing import List, Optional, Iterator, Dict
from pydantic import ConfigDict, BaseModel

import tracardi.service.wf
from tracardi.domain.entity import Entity

from .port_to_port_edges import PortToPortEdges
from ..service.node_indexer import index_nodes
from tracardi.service.plugin.domain.register import RunOnce, NodeEvents, MicroserviceConfig
from tracardi.service.plugin.runner import ActionRunner


class Graph(BaseModel):
    in_edges: PortToPortEdges = PortToPortEdges()
    out_edges: PortToPortEdges = PortToPortEdges()


class Node(Entity):
    name: str = None
    start: Optional[bool] = False
    debug: bool = False
    inputs: Optional[List[str]] = []
    outputs: Optional[List[str]] = []
    className: str
    module: str
    init: Optional[dict] = {}
    skip: bool = False
    run_once: Optional[RunOnce] = RunOnce()
    node: Optional[NodeEvents] = None
    block_flow: bool = False
    on_error_continue: bool = False
    run_in_background: bool = False
    on_connection_error_repeat: int = 1
    append_input_payload: bool = False
    join_input_payload: bool = False
    object: Optional[ActionRunner] = None
    microservice: Optional[MicroserviceConfig] = None
    remote: bool = False
    graph: Graph = Graph()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_input_edges(self) -> PortToPortEdges:
        return self.graph.in_edges

    def get_output_edges(self) -> PortToPortEdges:
        return self.graph.out_edges

    def get_number_of_input_edges(self) -> int:
        return len(self.get_input_edges().edges)

    def get_number_of_output_edges(self) -> int:
        return len(self.get_output_edges().edges)

    def get_input_nodes(self, nodes) -> Iterator[tracardi.service.wf.domain.flow_graph_data.Node]:
        index_of_nodes = index_nodes(nodes)  # type: Dict[str, tracardi.service.wf.domain.flow_graph_data.Node]
        for port_out, edge, port_in in self.get_input_edges():
            yield index_of_nodes[edge.source.node_id]

    def has_input_node(self, nodes, class_name) -> bool:
        for node in self.get_input_nodes(nodes):
            if node.data.spec.className == class_name:
                return True
        return False

    def is_microservice_configured(self) -> bool:
        return self.microservice is not None and self.microservice.server.resource.id and self.microservice.plugin.id
