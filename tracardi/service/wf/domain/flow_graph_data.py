import hashlib
from random import randint

from uuid import uuid4

from typing import List

from pydantic import BaseModel
from tracardi_plugin_sdk.domain.register import Plugin


class Position(BaseModel):
    x: int
    y: int


class SimplifiedSpec(BaseModel):
    module: str


class EdgeBundle:
    def __init__(self, source, edge, target):
        self.source = source
        self.edge = edge
        self.target = target

    def __repr__(self):
        return "EdgeBundle(source={}, edge=({}), target={}".format(self.source.id, self.edge, self.target.id)


class Node(BaseModel):
    id: str
    type: str
    position: Position
    data: Plugin

    def __call__(self, *args) -> 'NodePort':
        if len(args) == 0:
            raise ValueError("Port is missing.")
        if len(args) != 1:
            raise ValueError("Only one port is allowed.")

        return NodePort(node=self, port=args[0])

    def __rshift__(self, other):
        raise ValueError(
            "You can not connect with edge nodes. Only node ports can be connected. Use parentis to indicate node.")


class NodePort:
    def __init__(self, port: str, node: Node):
        self.node = node
        self.port = port

    def __rshift__(self, node_port: 'NodePort') -> EdgeBundle:

        if self.port not in self.node.data.spec.outputs:
            raise ValueError("Could not find port `{}` in defined output ports of `{}`. Allowed ports are: `{}`".format(
                self.port,
                self.node.data.spec.className,
                self.node.data.spec.outputs
            ))

        if node_port.port not in node_port.node.data.spec.inputs:
            raise ValueError("Could not find port `{}` in defined input ports of `{}`. Allowed ports are: `{}`".format(
                node_port.port,
                node_port.node.data.spec.className,
                node_port.node.data.spec.inputs
            ))

        node_port.node.position.y += randint(0, 500)
        node_port.node.position.x += randint(0, 500)

        edge = Edge(
            id=str(uuid4()),
            type="default",
            source=self.node.id,
            target=node_port.node.id,
            sourceHandle=self.port,
            targetHandle=node_port.port
        )
        return EdgeBundle(
            source=self.node,
            edge=edge,
            target=node_port.node
        )


class Edge(BaseModel):
    source: str
    sourceHandle: str
    target: str
    targetHandle: str
    id: str
    type: str

    def __eq__(self, other: 'Edge'):
        return other.source == self.source and \
               other.target == self.target and \
               other.type == self.type and \
               other.sourceHandle == self.sourceHandle and \
               other.targetHandle == self.targetHandle


class FlowGraphData(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

    def __add__(self, node: Node):
        self.nodes.append(node)

    def shorten_edge_ids(self):
        for edge in self.edges:
            if len(edge.id) > 32:
                edge.id = hashlib.md5(edge.id.encode()).hexdigest()

    def get_node_by_id(self, id) -> Node:
        for node in self.nodes:
            if node.id == id:
                return node

    def get_nodes_out_edges(self, node_id) -> List[Edge]:
        for edge in self.edges:
            if edge.source == node_id:
                yield edge

    def get_nodes_in_edges(self, node_id) -> List[Edge]:
        for edge in self.edges:
            if edge.target == node_id:
                yield edge

    def remove_out_edge_on_port(self, port):
        def __remove():
            for edge in self.edges:
                if edge.sourceHandle != port:
                    yield edge

        self.edges = list(__remove())
