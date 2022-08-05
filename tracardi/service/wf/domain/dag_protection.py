from ..utils.dag_error import DagGraphError

_global_executed_flows = []


def is_acyclic(flow_id):
    global _global_executed_flows
    if flow_id in _global_executed_flows:
        raise DagGraphError("Execution of flows is not acyclic. Flow id `{}` "
                                "makes a circle of `{}` -> {}".format(flow_id, _global_executed_flows, flow_id))
    _global_executed_flows.append(flow_id)
    return True


def reset_acyclic():
    global _global_executed_flows
    _global_executed_flows = []
