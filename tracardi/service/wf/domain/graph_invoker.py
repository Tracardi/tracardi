import asyncio
import inspect
import json
from collections import defaultdict

from time import time
from typing import List, Union, Tuple, Optional, Dict, AsyncIterable
from pydantic import BaseModel, ValidationError

from tracardi.domain import ExtraInfo
from tracardi.domain.enum.event_status import PROCESSED
from tracardi.exceptions.log_handler import get_logger

from tracardi.domain.event import Event
from tracardi.domain.event_session import EventSession
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.console import Log, ConsoleStatus
from tracardi.service.plugin.domain.result import Result, VoidResult, MissingResult
from traceback import format_exc

from .debug_call_info import Profiler
from .debug_info import DebugInfo, DebugNodeInfo
from .entity import Entity
from .error_debug_info import ErrorDebugInfo
from .input_params import InputParams
from ..service.excetions import get_traceback
import tracardi.service.wf.service.life_cycle as life_cycle
from ..utils.dag_error import DagError, DagExecError
from .edge import Edge
from .node import Node
from .tasks_results import ActionsResults
from ...notation.dict_traverser import DictTraverser
from ...notation.dot_accessor import DotAccessor
from ...utils.getters import get_entity_id
from ...value_threshold_manager import ValueThresholdManager

logger = get_logger(__name__)


class InputEdge(BaseModel):
    id: str
    active: bool
    port: str
    params: Optional[dict] = None


class InputEdges:

    def __init__(self):
        self.edges = {}  # type: Dict[str, InputEdge]

    def add_edge(self, id: str, edge: InputEdge):
        self.edges[id] = edge

    def has_active_edges(self) -> bool:
        for _, edge in self.edges.items():
            if edge.active is True:
                return True
        return False

    def has_edge(self, id) -> bool:
        return self.edges[id] if id in self.edges else False

    def get_first_edge(self) -> Optional[InputEdge]:
        edges_ids = list(self.edges.keys())
        if edges_ids:
            return self.edges[edges_ids[0]]
        return None

    def __len__(self):
        return len(self.edges)


class GraphInvoker(BaseModel):
    graph: List[Node]
    start_nodes: list
    debug: bool = False

    @staticmethod
    def _add_to_event_loop(tasks, coroutine, port, params, edge: Edge, active) -> list:
        task = asyncio.create_task(coroutine)
        tasks.append((task, port, params, edge, active))
        return tasks

    @staticmethod
    async def _void_return(node: Node):

        all_outputs = [VoidResult(port=_start_port, value=None)
                       for _start_port in node.outputs]

        outputs_len = len(all_outputs)

        if outputs_len == 0:
            return None
        elif len(all_outputs) == 1:
            return all_outputs[0]
        else:
            return tuple(all_outputs)

    @staticmethod
    async def _skip_node(node: Node, params):
        # Returns payload on every output port
        all_outputs = ([Result(port=_start_port, value=params)
                        for _start_port in node.outputs])

        outputs_len = len(all_outputs)

        if outputs_len == 0:
            return None
        elif len(all_outputs) == 1:
            return all_outputs[0]
        else:
            return tuple(all_outputs)

    @staticmethod
    def _null_params(node):
        pass

    async def _run_in_event_loop(self, tasks, node: Node, params, _port, _task_result, in_edge: Edge = None):
        try:

            params['in_edge'] = in_edge

            if node.skip is True:
                coroutine = self._skip_node(node, params)
            else:
                if node.run_once.enabled is True:

                    if node.object.profile is None:
                        node.object.console.log("Conditional stop is not connected with a profile (profiless event) and "
                                                "assigned to only to node {}{}".format(node.name, node.id))

                    profile_id = node.object.profile.id if node.object.profile is not None else None

                    vtm = ValueThresholdManager(
                        name=node.name,
                        node_id=node.id,
                        profile_id=profile_id,
                        ttl=node.run_once.ttl,
                        debug=self.debug
                    )

                    dot_payload = list(params.values())
                    dot = DotAccessor(profile=node.object.profile,
                                      session=node.object.session,
                                      payload=dot_payload[0] if len(dot_payload) == 1 else {},
                                      # this is fine, input params has only one value
                                      event=node.object.event,
                                      flow=node.object.flow,
                                      memory=node.object.memory)

                    if node.run_once.type == 'value':
                        value = dot[node.run_once.value]
                    elif node.run_once.type == 'condition':
                        condition = Condition()
                        value = await condition.evaluate(node.run_once.value, dot)
                    else:
                        raise ValueError("Unknown type {} for conditional workflow stop.".format(node.run_once.type))
                    if not await vtm.pass_threshold(value):
                        coroutine = self._void_return(node)
                        node.object.console.log(f"Node `{node.name}` stopped; Conditional value `{value}` have not changed.")
                    else:
                        coroutine = life_cycle.plugin.execute(node, params)
                        node.object.console.log(
                            f"Node `{node.name}` executed; Conditional value `{value}` have changed.")

                else:
                    coroutine = life_cycle.plugin.execute(node, params)
            return self._add_to_event_loop(tasks,
                                           coroutine,
                                           port=_port,
                                           params=_task_result,
                                           edge=in_edge if isinstance(in_edge, Edge) else None,
                                           active=True)
        except TypeError as e:
            args_spec = inspect.getfullargspec(node.object.run)
            method_params = args_spec.args[1:]
            if not set(method_params).intersection(set(params.keys())):
                raise DagExecError(
                    "Misconfiguration of node type `{}`. Method `run` expects input parameters `{}`, "
                    "but received `{}`. TypeError: `{}`".
                        format(node.className,
                               ",".join(method_params),
                               ",".join(params.keys()),
                               str(e)),
                    traceback=get_traceback(e)
                )

    def set_profiles(self, profile):
        """
        Sets reference to profile as None
        """
        for node in self.graph:
            if not isinstance(node.object, DagExecError):
                node.object.profile = profile
                if node.object.event:
                    node.object.event.profile = profile

    def set_sessions(self, session):
        """
        Sets reference to session as None
        """
        for node in self.graph:
            if not isinstance(node.object, DagExecError):
                node.object.session = session
                if node.object.event:
                    node.object.event.session = EventSession(
                        id=session.id,
                        start=session.metadata.time.insert,
                        duration=session.metadata.time.duration
                    ) if session is not None else None

    async def run_node(self, node: Node, payload, ready_upstream_results: ActionsResults) -> AsyncIterable[Tuple[
        Result, float, Optional[Profile], Optional[Session], ConsoleStatus, InputEdges]]:

        task_start_time = time()

        if isinstance(node.object, DagExecError):
            raise node.object

        tasks = []

        if node.start:

            # This is start node

            _port = "payload"
            _payload = {}

            params = {"payload": payload}

            logger.debug(f"Runs start node \"{node.name}\". ")

            tasks = await self._run_in_event_loop(tasks, node, params, _port, _payload, in_edge=None)

        elif node.graph.in_edges:

            # Prepare value

            for start_port, edge, end_port in node.graph.in_edges.get_enabled_edges():  # type: str, Edge, str

                if not ready_upstream_results.has_edge_value(edge.id):
                    # This edge is dead. Dead edges are connected to nodes that return None instead of Result object.
                    continue

                for upstream_result in ready_upstream_results.get(
                        edge.id,
                        start_port):  # type: Union[Result]

                    if isinstance(upstream_result, MissingResult):

                        # Missing result

                        void_result_coroutine = self._void_return(node)

                        # The original run method is replaced by _void_return function

                        tasks = self._add_to_event_loop(tasks,
                                                        void_result_coroutine,
                                                        end_port,
                                                        None,
                                                        edge,
                                                        active=False)

                    else:

                        upstream_result_copy = upstream_result.model_copy(deep=True)

                        # Do not trigger for None values

                        params = {end_port: upstream_result_copy.value}
                        if upstream_result_copy.value is not None:

                            # Run spec with every downstream message (param)
                            # Runs as many times as downstream edges

                            logger.debug(
                                f"Runs node \"{node.name}\". ",
                                extra=ExtraInfo.build(
                                    origin="workflow",
                                    object=self,
                                    node_id=node.id
                                )
                            )

                            tasks = await self._run_in_event_loop(
                                tasks,
                                node,
                                params,
                                end_port,
                                upstream_result.value,
                                in_edge=edge)

                        else:

                            # Missing result

                            void_result_coroutine = self._void_return(node)

                            # The original run method is replaced by _void_return function

                            tasks = self._add_to_event_loop(tasks,
                                                            void_result_coroutine,
                                                            end_port,
                                                            upstream_result.value,
                                                            edge,
                                                            active=False
                                                            )

        # Yield async tasks results

        joined_output_results = defaultdict(dict)
        joined_profile_reference = None
        joined_session_reference = None

        input_edges = InputEdges()

        for task, input_port, input_params, edge, active in tasks:

            input_edge_id = edge.id if edge is not None else None

            # Get previous session and profile. Session or profile can be overridden, so we need to be sure when the
            # reference has changed

            _current_profile_reference = node.object.profile
            _prev_profile_reference = node.object.profile

            _current_session_reference = node.object.session
            _prev_session_reference = node.object.session

            try:

                result = await task

                if node.append_input_payload:
                    result = Result.append_input(result, input_params)

                _current_profile_reference = node.object.profile
                _current_session_reference = node.object.session

                if not isinstance(_current_profile_reference,
                                  Profile) or _current_profile_reference is _prev_profile_reference:
                    _current_profile_reference = None

                if not isinstance(_current_session_reference,
                                  Session) or _current_session_reference is _prev_session_reference:
                    _current_session_reference = None

            except BaseException as e:

                if isinstance(node.object, ActionRunner):
                    await node.object.on_error(e)

                msg = f"{repr(e)}. Check run method of `{node.className}`\n\n" \
                      f"Details: {format_exc()}"

                result = DagExecError(
                    msg,
                    port=input_port,
                    input=input_params,
                    edge=input_edge_id,
                    traceback=get_traceback(e)
                )

            if node.object.join_output():

                """ Collect results """

                if isinstance(edge, Edge):

                    input_edges.add_edge(input_edge_id, InputEdge(id=input_edge_id, active=active, port=input_port,
                                                                  params=input_params))

                    key = edge.data.name if edge.has_name() else edge.id

                    joined_profile_reference = _current_profile_reference
                    joined_session_reference = _current_session_reference

                    if result:
                        """
                        Map port and payload by edge key
                        """
                        joined_output_results[result.port][key] = result.value

            else:

                """ Yield results one by one """

                _single_input_edge = InputEdges()

                if input_edge_id is not None:
                    """ Skip if there is no input edge """
                    try:
                        _single_input_edge.add_edge(input_edge_id,
                                                    InputEdge(id=input_edge_id,
                                                              active=active,
                                                              port=input_port,
                                                              params=input_params)
                                                    )
                    except ValidationError as e:
                        raise ValueError(f"Node name `{node.name}` received data that is not a object/dictionary. "
                                         f"Data come from edge name `{edge.name}`. "
                                         f"Expected dict got `{input_params}` of type {type(input_params)}. "
                                         f"Inner error: {str(e)}")

                yield result, \
                      task_start_time, \
                      _current_profile_reference, \
                      _current_session_reference, \
                      node.object.console.get_status(), _single_input_edge

        if node.object.join_output():

            """ Yield collected results """

            for out_port, out_payload in joined_output_results.items():

                # todo template per port

                if node.object.join.has_reshape_templates():
                    try:
                        output = json.loads(node.object.join.get_reshape_template(out_port).template)
                    except Exception as e:
                        raise ValueError(f"Error in join node. Could not parse reshape schema. Details: {str(e)}.")

                    if output:
                        dot = DotAccessor(
                            node.object.profile,
                            node.object.session,
                            out_payload if isinstance(out_payload, dict) else None,
                            node.object.event
                        )

                        if node.object.join.get_reshape_template(out_port).default is True:
                            template = DictTraverser(dot, default=None)
                        else:
                            template = DictTraverser(dot)

                        out_payload = template.reshape(reshape_template=output)

                yield Result(port=out_port,
                             value=out_payload), \
                      task_start_time, \
                      joined_profile_reference, \
                      joined_session_reference, \
                      node.object.console.get_status(), \
                      input_edges

    @staticmethod
    def _add_results(task_results: ActionsResults, node: Node, result: Result) -> ActionsResults:
        for _, edge, _ in node.graph.out_edges:
            result_copy = result.model_copy(deep=True)
            task_results.add(edge.id, result_copy)
        return task_results

    async def init(self, debug_info: DebugInfo, log_list: List[Log], flow, flow_history, event, session, profile,
                   tracker_payload: TrackerPayload,
                   ux: list):

        metrics = {}
        memory = {}

        for node_number, node in enumerate(self.graph):
            # Init object
            try:

                if node.remote is True and not node.is_microservice_configured():
                    raise RuntimeError("Microservice not configured. This node is a remote node but the remote "
                                       "microservice is not configured. See 'Remote microservice configuration' "
                                       "in node settings.")

                node.object = await life_cycle.plugin.create_instance(node)

                node.object = life_cycle.plugin.set_context(
                    node,
                    event,
                    session,
                    profile,
                    flow,
                    flow_history,
                    metrics,
                    memory,
                    ux,
                    tracker_payload,
                    self,
                    self.debug
                )

            except Exception as e:
                msg = "`{}`. This error occurred when initializing node `{}`. ".format(
                    str(e), node.name) + "Check node configuration, __init__, or post_init method of `{}.{}`".format(
                    node.module,
                    node.className)

                debug_info.flow.add_error(ErrorDebugInfo(
                    msg=msg, line=460, file=__file__
                ))
                debug_info.add_node_info(DebugNodeInfo(
                    id=node.id,
                    name=node.name,
                    sequenceNumber=node_number,
                    errors=1,
                    warnings=0,
                    profiler=Profiler(startTime=0, endTime=0, runTime=0)
                ))
                log_list.append(Log(
                    module=__name__,
                    class_name=GraphInvoker.__name__,
                    type='error',
                    message=msg,
                    node_id=node.id,
                    profile_id=get_entity_id(profile),
                    flow_id=get_entity_id(flow)
                ))
                node.object = DagExecError(
                    msg,
                    traceback=get_traceback(e)
                )

        return debug_info

    async def close(self):
        tasks = []
        for node in self.graph:
            if isinstance(node.object, ActionRunner):
                task = asyncio.create_task(node.object.close())
                tasks.append(task)
        await asyncio.gather(*tasks)

    @staticmethod
    def _get_input_params(input_port, input_params):
        if input_port:
            return InputParams(port=input_port, value=input_params)
        return None

    def is_in_debug_mode(self, event):
        """
        Is either event marked as debug or debug method was called
        """
        return event.metadata.debug is True or self.debug is True

    async def run(self,
                  payload: dict,
                  event: Event,
                  profile: Profile,
                  session: Session,
                  debug_info: DebugInfo,
                  log_list: List[Log],
                  ) -> Tuple[DebugInfo, List[Log], Profile, Session, Event]:

        actions_results = ActionsResults()
        flow_start_time = debug_info.timestamp

        sequence_number = 0
        execution_number = 0
        for node in self.graph:  # type: Node

            task_start_time = time()
            sequence_number += 1
            executed_node = False

            node_debug_info = DebugNodeInfo(
                id=node.id,
                name=node.name,
                sequenceNumber=sequence_number,
                executionNumber=None,
                errors=0,
                warnings=0,
                profiler=Profiler(
                    startTime=task_start_time,
                    endTime=task_start_time,
                    runTime=task_start_time
                ),
            )

            try:

                # Skip debug nodes when not debugging
                if not self.debug and node.debug:
                    continue

                # Skip tasks that are marked to be skipped
                if node.block_flow is True:
                    continue

                async for result, \
                          task_start_time, \
                          _profile_reference_to_update, _session_reference_to_update, \
                          node_console_status, input_edges in \
                        self.run_node(node, payload, ready_upstream_results=actions_results):

                    # If the profile or session changed during node execution change its reference in graph invoker

                    if _profile_reference_to_update:
                        profile = _profile_reference_to_update

                    if _session_reference_to_update:
                        session = _session_reference_to_update

                    executed_node = input_edges.has_active_edges() | executed_node

                    # Add information if ony of the input edge is active

                    debug_info.add_debug_edge_info(input_edges)

                    # Process result

                    if result is None:
                        # Result is None
                        pass
                    elif isinstance(result, Result):
                        if result.value is not None:
                            actions_results = self._add_results(actions_results, node, result)
                    elif isinstance(result, tuple):
                        for sub_result in result:  # type: Result
                            if sub_result is None:
                                # This is None result
                                pass
                            elif isinstance(sub_result, Result):
                                if sub_result.value is not None:
                                    # Result is proper object
                                    actions_results = self._add_results(actions_results, node, sub_result)
                            else:
                                _edge = input_edges.get_first_edge()
                                raise DagError(
                                    "Action did not return Result or tuple of Results. Expected Result got {}".format(
                                        type(result)),
                                    port=_edge.port,
                                    input=_edge.params,
                                    edge=_edge.id
                                )
                    else:
                        # result can be DagExecError this means that this node raised exception
                        if isinstance(result, DagExecError):
                            raise result

                        _edge = input_edges.get_first_edge()

                        raise DagError(
                            "Action did not return Result or tuple of Results. Expected Result got {}".format(
                                type(result)),
                            port=_edge.port,
                            input=_edge.params,
                            edge=_edge.id
                        )

                    if self.is_in_debug_mode(event):
                        for input_edge_id, input_edge in input_edges.edges.items():  # type: str, InputEdge
                            node_debug_info.append_call_info(
                                flow_start_time,
                                task_start_time,
                                node,
                                input_edge=Entity(id=input_edge_id) if input_edge_id is not None else None,
                                input_params=self._get_input_params(input_edge.port, input_edge.params),
                                output_edge=None,
                                output_params=[result] if isinstance(result, Result) else result,
                                active=input_edge.active,
                                errors=node_console_status.errors,
                                warnings=node_console_status.warnings
                            )

                    if executed_node:
                        for input_edge_id, _ in input_edges.edges.items():  # type: str, InputEdge
                            log_list.append(
                                Log(
                                    node_id=node_debug_info.id,
                                    module=node.object.console.module,
                                    class_name=node.object.console.class_name,
                                    type='debug',
                                    message=f"Node `{node_debug_info.name}` edge {input_edge_id} executed without errors."
                                )
                            )

            except (DagError, DagExecError) as e:

                error_log = Log(
                    profile_id=get_entity_id(profile),
                    node_id=node.id,
                    module=__name__,
                    class_name='GraphInvoker',
                    type='error',
                    message=str(e)
                )

                if isinstance(e, DagExecError):
                    error_log.traceback = e.traceback
                elif isinstance(e, DagError):
                    error_log.traceback = get_traceback(e)

                log_list.append(error_log)

                if self.is_in_debug_mode(event):
                    if e.input is not None and e.port is not None:

                        node_debug_info.append_call_info(
                            flow_start_time,
                            task_start_time,
                            node,
                            input_edge=Entity(id=e.edge) if e.edge is not None else None,
                            input_params=InputParams(port=e.port, value=e.input),
                            output_edge=None,
                            output_params=None,
                            active=True,
                            error=str(e),
                            errors=1,
                            warnings=0
                        )

                    else:

                        node_debug_info.append_call_info(
                            flow_start_time,
                            task_start_time,
                            node,
                            input_edge=Entity(id=e.edge) if e.edge is not None else None,
                            input_params=None,
                            output_edge=None,
                            output_params=None,
                            active=True,
                            error=str(e),
                            errors=1,
                            warnings=0
                        )

                # Stop workflow when there is an error
                break

            finally:
                if self.is_in_debug_mode(event):
                    node_debug_info.profiler.endTime = time() - flow_start_time
                    node_debug_info.profiler.runTime = time() - flow_start_time - task_start_time

                    # If node had call that means it was running

                    if executed_node:
                        execution_number += 1
                        node_debug_info.executionNumber = execution_number
                        # debug_info.nodes[node_debug_info.id] = node_debug_info
                        debug_info.add_node_info(node_debug_info)

                # Collect console logs set inside plugins
                if isinstance(node.object, ActionRunner):

                    if node.object.console.warnings:
                        event.metadata.warning = True

                    if node.object.console.errors:
                        event.metadata.error = True

                    for log in node.object.console.get_logs():  # type: Log
                        log_list.append(log)

        event.metadata.status = PROCESSED
        # Sum up all process WF times
        event.metadata.time.process_time = event.metadata.time.process_time + (time() - flow_start_time)

        return debug_info, log_list, profile, session, event

    def serialize(self):
        return self.model_dump()

    def get_node_by_id(self, node_id) -> Node:
        for node in self.graph:
            if node.id == node_id:
                return node
