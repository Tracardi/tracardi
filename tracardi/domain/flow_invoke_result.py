from typing import Optional, List

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.console import Log
from tracardi.service.wf.domain.debug_info import DebugInfo
from tracardi.service.wf.domain.flow import Flow


class FlowInvokeResult:

    def __init__(self, debug_info: DebugInfo, log_list: List[Log], flow: Flow, event: Event,
                 profile: Optional[Profile] = None,
                 session: Optional[Session] = None):
        self.debug_info = debug_info
        self.log_list = log_list
        self.event = event
        self.profile = profile
        self.session = session
        self.flow = flow

    def __repr__(self):
        return f"FlowInvokeResult(\n\tprofile=({self.profile})\n\tsession=({self.session})\n\tevent=({self.event}))"
