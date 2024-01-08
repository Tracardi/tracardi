from typing import Dict, List
from tracardi.domain.event import Event
from tracardi.process_engine.debugger import Debugger


class RuleInvokeResult:

    def __init__(self, debugger: Debugger, ran_event_types: List[str],
                 post_invoke_events: Dict[str, Event],
                 invoked_rules: Dict[str, List[str]],
                 invoked_flows: List[str],
                 flow_responses: List[dict],
                 changes_timestamps: List[dict]):
        self.flow_responses: List[dict] = flow_responses
        self.invoked_rules: Dict[str, List[str]] = invoked_rules
        self.invoked_flows: List[str] = invoked_flows
        self.post_invoke_events: Dict[str, Event] = post_invoke_events
        self.ran_event_types: List[str] = ran_event_types
        self.debugger:Debugger = debugger
        self.changes_timestamps:List[dict] = changes_timestamps

