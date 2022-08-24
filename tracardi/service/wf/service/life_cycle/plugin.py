import importlib
from typing import Optional

from tracardi.domain.event import Event
from tracardi.domain.flow import Flow
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.console import Console
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.wf.domain.node import Node


async def create_instance(node: Node, params: dict, debug: bool) -> ActionRunner:
    """
    Creates plugin instance
    """

    async def _build(debug: bool, plugin_class, params: dict):
        build_method = getattr(plugin_class, "build", None)

        if params:
            params['__debug__'] = debug
        else:
            params = {'__debug__': debug}

        if callable(build_method):
            return await build_method(**params)

        return plugin_class(**params)

    module = importlib.import_module(node.module)
    node_class = getattr(module, node.className)
    action = await _build(debug, node_class, params)

    if not isinstance(action, ActionRunner):
        raise TypeError("Class {}.{} is not of type {}".format(module, node.className, type(ActionRunner)))

    return action


def set_context(node: Node,
                event: Optional[Event],
                session: Optional[Session],
                profile: Optional[Profile],
                flow: Optional[Flow],
                flow_history,
                metrics,
                memory,
                ux,
                tracker_payload: TrackerPayload,
                execution_graph,
                debug: bool) -> ActionRunner:
    node.object.node = node.copy(exclude={"object": ..., "className": ..., "module": ..., "init": ...})
    node.object.debug = debug
    node.object.event = event
    node.object.session = session
    node.object.profile = profile
    node.object.flow = flow
    node.object.flow_history = flow_history
    node.object.console = Console(node.className, node.module)
    node.object.id = node.id
    node.object.metrics = metrics
    node.object.memory = memory
    node.object.ux = ux
    node.object.tracker_payload = tracker_payload
    node.object.execution_graph = execution_graph

    return node.object


async def execute(node: Node, params: dict) -> Optional[Result]:
    # params has payload and in_edge
    return await node.object.run(**params)
