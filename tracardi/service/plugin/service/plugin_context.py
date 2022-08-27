from typing import List

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.wf.domain.node import Node


def get_context(plugin: ActionRunner, include: List[str] = None) -> dict:
    if include is None:
        include = []

    return {
        "id": plugin.id,
        "debug": plugin.debug,
        "event": plugin.event.dict() if plugin.event else None,
        "session": plugin.session.dict() if plugin.session else None,
        "profile": plugin.profile.dict() if plugin.profile else None,
        "metrics": plugin.metrics,
        "memory": plugin.memory,
        "node": plugin.node.dict() if 'node' in include else None,
        "flow": plugin.flow.dict() if 'flow' in include and plugin.flow else None,
        "flow_history": plugin.flow_history if 'flow_history' in include else None,
        "execution_graph": plugin.execution_graph.dict() if 'execution_graph' in include else None,
        "tracker_payload": plugin.tracker_payload.dict() if 'tracker_payload' in include and plugin.tracker_payload else None,
        "ux": plugin.ux,
        "join": plugin.join
    }


def set_context(plugin: ActionRunner, context: dict, include: List[str] = None):
    if include is None:
        include = []
    plugin.event = Event(**context['event']) if context['event'] is not None else None
    plugin.session = Session(**context['session']) if context['session'] is not None else None
    plugin.profile = Profile(**context['profile']) if context['profile'] is not None else None
    plugin.metrics = context['metrics']
    plugin.memory = context['memory']
    plugin.ux = context['ux']
    # # Id, debug, node, flow, execution_graph, tracker_payload, and join should not be restored as they are read only
    # # They can be restored only if on remote server
    plugin.node = Node(**context['node']) if context['node'] is not None and 'node' in include else None
