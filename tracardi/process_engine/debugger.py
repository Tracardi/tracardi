from collections import defaultdict

from tracardi.service.wf.domain.debug_info import DebugInfo


class Debugger:

    def __init__(self):
        self.traces = defaultdict(list)

    def has_node_debug_trace(self):
        return len(self.traces) > 0

    def has_call_debug_trace(self):
        for event_type, list_of_rule_and_debug_info in self.traces.items():
            for debug_info_and_rule in list_of_rule_and_debug_info:  # type: dict
                for rule_name, debug_info in debug_info_and_rule.items():  # type: DebugInfo
                    if debug_info.has_nodes():
                        return True
        return False

    def __setitem__(self, key, value):
        self.traces[key].append(value)

    def __getitem__(self, item):
        return self.traces[item]

    def __contains__(self, item):
        return item in self.traces

    def items(self):
        return self.traces.items()

