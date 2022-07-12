from typing import List, Dict, Optional
from pydantic import BaseModel
from time import time
from .debug_call_info import DebugCallInfo, Profiler, DebugInput, DebugOutput
from .entity import Entity
from .error_debug_info import ErrorDebugInfo
from .input_params import InputParams
from ...plugin.runner import ActionRunner


class FlowDebugInfo(Entity):
    name: str = "unknown"
    error: List[ErrorDebugInfo] = []

    def has_errors(self) -> bool:
        return len(self.error) > 0

    def add_error(self, error: ErrorDebugInfo):
        self.error.append(error)


class DebugNodeInfo(BaseModel):
    id: str
    name: str = None
    sequenceNumber: int = None
    executionNumber: Optional[int] = None
    errors: int = 0
    warnings: int = 0
    calls: List[DebugCallInfo] = []
    profiler: Profiler

    def has_errors(self) -> bool:
        for call in self.calls:
            if call.has_error():
                return True
        return False

    @staticmethod
    def _get_input_params(input_port, input_params):
        if input_port:
            return InputParams(port=input_port, value=input_params)
        return None

    def append_call_info(self, flow_start_time, task_start_time,
                         node,
                         input_edge: Entity,
                         input_params: Optional[InputParams],
                         output_edge: Optional[Entity],
                         output_params: Optional[InputParams],
                         active,
                         error=None,
                         errors=0,
                         warnings=0):

        debug_start_time = task_start_time - flow_start_time
        debug_end_time = time() - flow_start_time
        debug_run_time = debug_end_time - debug_start_time

        call_debug_info = DebugCallInfo(

            run=active,

            profiler=Profiler(
                startTime=debug_start_time,
                endTime=debug_end_time,
                runTime=debug_run_time
            ),

            input=DebugInput(
                edge=input_edge,
                params=input_params
            ),
            output=DebugOutput(
                edge=output_edge,  # todo this is always none
                results=output_params
            ),

            init=node.init,
            profile=node.object.profile.dict() if isinstance(node.object, ActionRunner) and isinstance(
                node.object.profile, BaseModel) else {},

            event=node.object.event.dict() if isinstance(node.object, ActionRunner) and isinstance(node.object.event,
                                                                                                   BaseModel) else {},
            session=node.object.session.dict() if isinstance(node.object, ActionRunner) and isinstance(
                node.object.session, BaseModel) else {},
            error=error,

            errors=errors,
            warnings=warnings
        )

        self.warnings += warnings
        self.errors += errors
        self.calls.append(call_debug_info)


class DebugEdgeInfo(BaseModel):
    active: List[bool] = []


class DebugInfo(BaseModel):
    timestamp: float
    flow: FlowDebugInfo
    # rule: str
    event: Entity
    nodes: Dict[str, DebugNodeInfo] = {}
    edges: Dict[str, DebugEdgeInfo] = {}

    def _add_debug_edge_info(self, input_edge_id, active):
        if input_edge_id not in self.edges:
            self.edges[input_edge_id] = DebugEdgeInfo(
                active=[active]
            )
        else:
            self.edges[input_edge_id].active.append(active)

    def add_debug_edge_info(self, input_edges):
        for edge_id, edge in input_edges.edges.items(): # type: str, InputEdge
            self._add_debug_edge_info(edge_id, edge.active)

    def add_node_info(self, info: DebugNodeInfo):
        self.nodes[info.id] = info

    def has_nodes(self):
        return len(self.nodes) > 0

    def has_errors(self) -> bool:
        if self.flow.has_errors():
            return True

        for _, node in self.nodes.items():
            if node.has_errors():
                return True
        return False
