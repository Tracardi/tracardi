from typing import Dict, List

from tracardi.domain.console import Console
from tracardi.domain.event import Event
from tracardi.process_engine.debugger import Debugger


class RuleInvokeResult:

    def __init__(self, debugger: Debugger, ran_event_types: List[str], console_log: List[Console],
                 post_invoke_events: Dict[str, Event], invoked_rules: Dict[str, List[str]], flow_responses: List[dict]):
        self.flow_responses = flow_responses
        self.invoked_rules = invoked_rules
        self.post_invoke_events = post_invoke_events
        self.console_log = console_log
        self.ran_event_types = ran_event_types
        self.debugger = debugger

