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
        "event": plugin.event.model_dump(mode='json') if plugin.event else None,
        "session": plugin.session.model_dump(mode='json') if plugin.session else None,
        "profile": plugin.profile.model_dump(mode='json') if plugin.profile else None,
        "metrics": plugin.metrics,
        "memory": plugin.memory,
        "node": plugin.node.model_dump(mode='json') if 'node' in include else None,
        "flow": plugin.flow.model_dump(mode='json') if 'flow' in include and plugin.flow else None,
        "flow_history": plugin.flow_history if 'flow_history' in include else None,
        "execution_graph": plugin.execution_graph.model_dump(mode='json') if 'execution_graph' in include else None,
        "tracker_payload": plugin.tracker_payload.model_dump(mode='json') if 'tracker_payload' in include and plugin.tracker_payload else None,
        "ux": plugin.ux,
        "join": plugin.join
    }


def set_context(plugin: ActionRunner, context: dict, include: List[str] = None):

    if include is None:
        include = []

    if context['event'] is not None:
        # Event can be None if plugin on remote server
        if plugin.event is None:
            plugin.event = Event(**context['event'])
        else:
            plugin.event.replace(Event(**context['event']))

    if context['session'] is not None:
        if plugin.session is None:
            plugin.session = Session(**context['session'])
        else:
            plugin.session.replace(Session(**context['session']))

    if context['profile'] is not None:
        if plugin.profile is None:
            plugin.profile = Profile(**context['profile'])
        else:
            plugin.profile.replace(Profile(**context['profile']))

    if isinstance(context['metrics'], dict):
        if plugin.metrics is None:
            plugin.metrics = {}
        plugin.metrics.update(**context['metrics'])

    if isinstance(context['memory'], dict):
        if plugin.memory is None:
            plugin.memory = {}
        plugin.memory.update(**context['memory'])

    if isinstance(context['ux'], list):
        if plugin.ux is None:
            plugin.ux = []
        for ux in context['ux']:
            if ux not in plugin.ux:
                plugin.ux.append(ux)

    # # Id, debug, node, flow, execution_graph, tracker_payload, and join should not be restored as they are read only
    # # They can be restored only if on remote server
    plugin.node = Node(**context['node']) if context['node'] is not None and 'node' in include else None
