from typing import List
from pydantic import BaseModel
from .edge import Edge
from .node import Node


class DagGraph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
