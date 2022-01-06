from typing import List

from tracardi_plugin_sdk.domain.result import Result, MissingResult
from ..utils.dag_error import DagError


class ResultStorage(dict):

    def port(self, port):
        return self[port]


class ActionsResults:

    def __init__(self):
        self._results = {}

    def add(self, edge_id: str, result: Result):

        if edge_id not in self._results:
            self._results[edge_id] = {}

        if result.port not in self._results[edge_id]:
            self._results[edge_id][result.port] = []

        self._results[edge_id][result.port].append(result)

    def get(self, edge_id, port) -> List[Result]:

        if not self.has_edge_value(edge_id):
            raise DagError(
                "Expected output for edge {}, but none is present. Node not initiated properly or execution failed.".format(
                    edge_id), port=port)

        if port not in self._results[edge_id]:
            return [MissingResult(port=port, value=None)]
            # raise DagError("Edge {} did not return value in input_port {}.".format(edge_id, port), port=port)

        return self._results[edge_id][port]

    def copy(self):
        ts = ActionsResults()
        ts._results = self._results
        return ts

    def has_edge_value(self, edge_id) -> bool:
        return edge_id in self._results
