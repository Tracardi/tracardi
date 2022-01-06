from typing import Tuple, List

from .debug_info import DebugInfo
from .flow import Flow
from .flow_history import FlowHistory
from ..utils.dag_error import DagGraphError
from ..utils.dag_processor import DagProcessor
from ..utils.flow_graph_converter import FlowGraphConverter
from tracardi_plugin_sdk.domain.console import Log


class WorkFlow:

    def __init__(self, flow_history: FlowHistory, session, profile):
        self.flow_history = flow_history
        self.profile = profile
        self.session = session

    async def invoke(self, flow: Flow, event, ux: list, debug=False) -> Tuple[DebugInfo, List[Log], 'Event']:

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

            # Init and run with event
            await exec_dag.init(flow, self.flow_history, event, self.session, self.profile, ux)

            debug_info, log_list = await exec_dag.run(
                payload={},
                flow_id=flow.id,
                event_id=event.id
            )

            await exec_dag.close()

            return debug_info, log_list, event

        raise RuntimeError("Workflow has circular reference.")
