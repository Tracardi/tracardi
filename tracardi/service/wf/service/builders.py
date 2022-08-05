from uuid import uuid4

import inspect

from tracardi.service.wf.domain.flow_graph_data import Node, Position
from tracardi.service.plugin.runner import ActionRunner


def action(plugin, init=None) -> Node:
    if not isinstance(plugin, type):
        raise ValueError("Only references to objects can be added as workflow nodes.")
    if not inspect.isclass(ActionRunner):
        raise ValueError("Only plugins that extend ActionRunner can be added as workflow nodes.")

    module = inspect.getmodule(plugin)
    register = getattr(module, 'register')
    node = Node(
        id=str(uuid4()),
        type="flowNode",
        position=Position(x=440, y=80),
        data=register()
    )
    node.data.spec.init = init
    return node
