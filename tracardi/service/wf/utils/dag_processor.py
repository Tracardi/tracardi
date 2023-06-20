from typing import List, Union, Tuple

from .dag_error import DagGraphError
from ..domain.edge import Edge
from ..domain.edges import Edges
from ..domain.graph_invoker import GraphInvoker
from ..domain.dag_graph import DagGraph
from ..domain.node import Node
from ..domain.nodes import Nodes
from .dag_graph_sorter import DagGraphSorter


class DagProcessor:

    def __init__(self, flow: DagGraph):
        self._nodes = Nodes({node.id: node for node in flow.nodes})  # type: Union[List[Node], Nodes]
        self._edges = Edges()  # type: Union[List[Edge], Edges]
        for edge in flow.edges:
            self._edges[edge.__hash__()] = edge

        self._edges.validate(self._nodes)
        self._last_nodes = set()

    def _find_out_edges(self, node: Node) -> List[Tuple[str, Edge]]:
        for _, edge in self._edges.items():  # type: str, Edge
            if node.id == edge.source.node_id:
                yield edge.source.param, edge

    def _find_in_edges(self, node) -> List[Tuple[str, Edge]]:
        for _, edge in self._edges.items():  # type: str, Edge
            if node.id == edge.target.node_id:
                yield edge.target.param, edge

    def _find_node(self, node_id) -> Node:
        return self._nodes[node_id] if node_id in self._nodes else None

    def find_start_nodes(self) -> List[Node]:
        for _, node in self._nodes.items():
            if node.start:
                yield node

    def find_scheduled_nodes(self, node_ids: List[str]) -> List[Node]:
        for _, node in self._nodes.items():
            # All nodes are not start nodes except the scheduled node.
            node.start = False
            if node.id in node_ids:
                node.start = True
                yield node

    def _forward_pass(self, start_node_ids):
        for start_node_id in start_node_ids:
            node = self._find_node(start_node_id)  # type: Node
            if node:

                # Get edges
                edges = list(self._find_out_edges(node))

                if edges:
                    for edge_start_port, edge in edges:
                        if edge.target.node_id in self._nodes:  # type: Node

                            node.graph.out_edges.add(edge)

                            self._forward_pass([edge.target.node_id])
                else:
                    self._last_nodes.add(node.id)
            else:
                self._last_nodes.add(start_node_id)

        return self._last_nodes

    def _back_pass(self, last_node_ids):
        for last_node_id in last_node_ids:
            node = self._find_node(last_node_id)
            if node:
                for edge_end_port, edge in self._find_in_edges(node):  # type: str, Edge

                    node.graph.in_edges.add(edge)

                    self._back_pass([edge.source.node_id])

    def make_execution_dag(self, start_nodes, debug=False) -> GraphInvoker:
        self._last_nodes = set()
        start_node_ids = [node.id for node in start_nodes]

        if len(start_node_ids) == 0:
            raise DagGraphError("There is not start action or scheduled node in workflow graph ")

        # Finds outputs
        self._forward_pass(start_node_ids)
        # Finds inputs
        self._back_pass(self._last_nodes)

        # Todo it sort all nodes except the nodes after start node

        # Sort graph
        nodes = set(self._nodes.keys())
        graph = DagGraphSorter(nodes)
        for _, edge in self._edges.items():  # type: Edge
            graph.add_edge(edge.source.node_id, edge.target.node_id)

        sorted = graph.topological_sort()
        sorted_nodes = [self._nodes[s] for s in sorted if s in self._nodes]

        return GraphInvoker(graph=sorted_nodes, start_nodes=start_node_ids, debug=debug)
