from pydantic import BaseModel

from ..utils.dag_error import DagGraphError


class FlowHistory(BaseModel):
    history: list = []

    def is_acyclic(self, flow_id):
        if flow_id in self.history:
            raise DagGraphError("Execution of flows is not acyclic. Flow id `{}` "
                                "makes a circle of `{}` -> {}".format(flow_id, self.history, flow_id))
        self.history.append(flow_id)
        return True

    def reset_acyclic(self):
        self.history = []
