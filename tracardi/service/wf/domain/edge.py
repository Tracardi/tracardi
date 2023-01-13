from pydantic import BaseModel

from .connection import Connection
from .flow_graph_data import EdgeData
from ..utils.dag_error import DagError


class Edge(BaseModel):
    id: str
    source: Connection
    target: Connection
    enabled: bool = True
    data: EdgeData = EdgeData()

    def is_valid(self, nodes):
        if self.target.node_id not in nodes:
            raise DagError("Target node_id {} does not exist.".format(self.target.node_id), port=self.target.param)
        if self.source.node_id not in nodes:
            raise DagError("Source node_id {} does not exist.".format(self.source.node_id), port=self.source.param)

    def has_name(self):
        return self.data is not None and self.data.name != "" and self.data.name is not None

    @property
    def name(self) -> str:
        return self.data.name if self.has_name() else "No name"

    def __key(self):
        return self.source.node_id, self.source.param, self.target.node_id, self.target.param

    def __hash__(self):
        return hash(self.__key())
