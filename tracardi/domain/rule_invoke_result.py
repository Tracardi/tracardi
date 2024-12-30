from typing import Dict, List
from tracardi.domain.event import Event
from tracardi.process_engine.debugger import Debugger


class RuleInvokeResult:

    def __init__(self, debugger: Debugger, ran_event_types: List[str],
                 post_invoke_events: Dict[str, Event],
                 invoked_rules: Dict[str, List[str]],
                 invoked_flows: List[str],
                 flow_responses: List[dict],
                 changed_fields: Dict[str, List],
                 ux: List):
        self.flow_responses: List[dict] = flow_responses
        self.invoked_rules: Dict[str, List[str]] = invoked_rules
        self.invoked_flows: List[str] = invoked_flows
        self.post_invoke_events: Dict[str, Event] = post_invoke_events
        self.ran_event_types: List[str] = ran_event_types
        self.debugger: Debugger = debugger
        self.changed_fields: Dict[str, List] = changed_fields
        self.ux = ux


    def __repr__(self):
        return (f"RuleInvokeResult(flow_responses={self.flow_responses}, "
                f"invoked_rules={dict(self.invoked_rules)}, "
                f"invoked_flows={self.invoked_flows}), "
                f"event_types={self.ran_event_types}, "
                f"changed_fields={self.changed_fields}, "
                f"ux={bool(self.ux)}")
