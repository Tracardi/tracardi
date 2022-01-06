from typing import List, Dict, Optional
from pydantic import BaseModel

from .debug_call_info import DebugCallInfo, Profiler
from .entity import Entity
from .error_debug_info import ErrorDebugInfo


class FlowDebugInfo(Entity):
    error: List[ErrorDebugInfo] = []

    def has_errors(self) -> bool:
        return len(self.error) > 0


class DebugNodeInfo(BaseModel):
    id: str
    name: str = None
    sequenceNumber: int = None
    executionNumber: Optional[int] = None
    calls: List[DebugCallInfo] = []
    profiler: Profiler

    def has_errors(self) -> bool:
        for call in self.calls:
            if call.has_error():
                return True
        return False


class DebugEdgeInfo(BaseModel):
    active: List[bool] = []


class DebugInfo(BaseModel):
    timestamp: float
    flow: FlowDebugInfo
    event: Entity
    nodes: Dict[str, DebugNodeInfo] = {}
    edges: Dict[str, DebugEdgeInfo] = {}

    def add_debug_edge_info(self, input_edge_id, active):
        if input_edge_id is not None:
            if input_edge_id not in self.edges:
                self.edges[input_edge_id] = DebugEdgeInfo(
                    active=[active]
                )
            else:
                self.edges[input_edge_id].active.append(active)

    def has_errors(self) -> bool:
        if self.flow.has_errors():
            return True

        for _, node in self.nodes.items():
            if node.has_errors():
                return True
        return False
