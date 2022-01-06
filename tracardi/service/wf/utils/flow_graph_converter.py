import importlib

from ..domain.flow_graph_data import FlowGraphData
from ..domain.connection import Connection
from ..domain.edge import Edge
from ..domain.dag_graph import DagGraph
from ..domain.node import Node


class FlowGraphConverter:

    def __init__(self, flow: dict):
        self.data = FlowGraphData(**flow)

    def convert_to_dag_graph(self) -> DagGraph:
        nodes = []
        for node in self.data.nodes:

            n = Node(
                id=node.id,
                name=node.data.metadata.name,
                start=node.data.start,
                debug=node.data.debug,
                inputs=node.data.spec.inputs,
                outputs=node.data.spec.outputs,
                className=node.data.spec.className,
                module=node.data.spec.module,
                init=node.data.spec.init,
                on_error_continue=node.data.spec.on_error_continue,
                on_error_repeat=node.data.spec.on_error_repeat,
                append_input_payload=node.data.spec.append_input_payload,
                join_input_payload=node.data.spec.join_input_payload
            )

            nodes.append(n)

        edges = [Edge(
            id=edge.id,
            source=Connection(node_id=edge.source, param=edge.sourceHandle),
            target=Connection(node_id=edge.target, param=edge.targetHandle)
        ) for edge in self.data.edges]

        return DagGraph(nodes=nodes, edges=edges)
