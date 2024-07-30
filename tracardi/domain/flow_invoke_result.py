from typing import Optional, List

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.plugin.domain.console import Log
from tracardi.service.wf.domain.debug_info import DebugInfo
from tracardi.service.wf.domain.flow_graph import FlowGraph

logger = get_logger(__name__)


class FlowInvokeResult:

    def __init__(self, debug_info: DebugInfo, log_list: List[Log], flow: FlowGraph, event: Event,
                 profile: Optional[Profile] = None,
                 session: Optional[Session] = None):
        self.debug_info = debug_info
        self.log_list: List[Log] = log_list
        self.event = event
        self.profile = profile
        self.session = session
        self.flow = flow

    def __repr__(self):
        return f"FlowInvokeResult(\n\tprofile=({self.profile})\n\tsession=({self.session})\n\tevent=({self.event}))"

    def register_logs_in_logger(self):
        for log in self.log_list:
            if log.is_error():
                logger.error(
                    log.message,
                    extra=log.to_extra()
                )
            elif log.is_waring():
                logger.warning(
                    log.message,
                    extra=log.to_extra()
                )
            elif log.is_debug():
                logger.debug(
                    log.message,
                    extra=log.to_extra()
                )
