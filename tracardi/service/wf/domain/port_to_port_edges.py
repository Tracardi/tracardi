from typing import Tuple

from pydantic import BaseModel

from .edge import Edge
from .edges import Edges


class PortToPortEdges(BaseModel):
    edges: dict = {}

    def __iter__(self) -> Tuple[str, Edge, str]:
        for start, edges in self.edges.items():  # type: str, Edges
            for edge in edges:
                yield edge.source.param, edge, edge.target.param

    def get_enabled_edges(self) -> Tuple[str, Edge, str]:
        for start_port, edge, end_port in self:
            if edge.enabled is True:
                yield start_port, edge, end_port

    def __len__(self):
        i = 0
        for _, edges in self.edges.items():
            i += len(edges)
        return i

    def add(self, edge: Edge):
        if edge.source.param not in self.edges:
            self.edges[edge.source.param] = set()
        self.edges[edge.source.param].add(edge)

    def dict(self, **kwargs):
        for key, edge in self.edges.items():  # type: Edge
            self.edges[key] = list(self.edges[key])
        return super().dict(**kwargs)

    def get_start_ports(self):
        return self.edges.keys()

    def set_edges_on_port(self, port, enable: bool = True):
        """
        Enables or disables edges that start from port.

        :param port:
        :param enable:
        :return:
        """
        for start, edges in self.edges.items():  # type: str, Edges
            for edge in edges:
                if edge.source.param == port:
                    edge.enabled = enable

    def set_edges(self, enable: bool = True):
        """
        Enables or disables edges
        :param enable:
        :return:
        """
        for start, edges in self.edges.items():  # type: str, Edges
            for edge in edges:
                edge.enabled = enable
