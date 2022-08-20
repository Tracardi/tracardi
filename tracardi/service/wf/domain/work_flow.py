from time import time
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.flow_invoke_result import FlowInvokeResult
from tracardi.domain.payload.tracker_payload import TrackerPayload
from .debug_info import DebugInfo, FlowDebugInfo
from .flow import Flow
from .flow_history import FlowHistory
from ..utils.dag_error import DagGraphError
from ..utils.dag_processor import DagProcessor
from ..utils.flow_graph_converter import FlowGraphConverter


class WorkFlow:

    def __init__(self, flow_history: FlowHistory, tracker_payload: TrackerPayload = None):
        self.tracker_payload = tracker_payload
        self.flow_history = flow_history

    async def invoke(self, flow: Flow, event: Event, profile, session, ux: list, debug=False) -> FlowInvokeResult:

        """
        Invokes workflow and returns DebugInfo and list of saved Logs.
        """

        if event is None:
            raise DagGraphError(
                "Flow `{}` has no context event defined.".format(
                    flow.id))

        if not flow.flowGraph:
            raise DagGraphError("Flow {} is empty".format(flow.id))

        if self.flow_history.is_acyclic(flow.id):

            # Convert Editor graph to exec graph
            converter = FlowGraphConverter(flow.flowGraph.dict())
            dag_graph = converter.convert_to_dag_graph()
            dag = DagProcessor(dag_graph)

            try:
                exec_dag = dag.make_execution_dag(debug=debug)
            except DagGraphError as e:
                raise DagGraphError("Flow `{}` returned the following error: `{}`".format(flow.id, str(e)))

            flow_start_time = time()
            debug_info = DebugInfo(
                timestamp=flow_start_time,
                flow=FlowDebugInfo(id=flow.id, name=flow.name),
                event=Entity(id=event.id)
            )
            log_list = []

            # Init and run with event
            debug_info = await exec_dag.init(
                debug_info,
                log_list,
                flow,
                self.flow_history,
                event,
                session,
                profile,
                self.tracker_payload,
                ux)

            if not debug_info.has_errors():

                debug_info, log_list, profile, session = await exec_dag.run(
                    payload={},
                    event=event,
                    profile=profile,
                    session=session,
                    debug_info=debug_info,
                    log_list=log_list
                )

            await exec_dag.close()

            return FlowInvokeResult(debug_info, log_list, flow, event, profile, session)

        raise RuntimeError("Workflow has circular reference.")
