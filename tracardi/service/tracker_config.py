from dataclasses import dataclass
from typing import List, Callable, Any, Dict

from tracardi.domain.event_source import EventSource
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.profile import Profile
from tracardi.service.console_log import ConsoleLog


@dataclass
class TrackerConfig:
    ip: str
    allowed_bridges: List[str]
    on_source_ready: Callable[[Dict[str, List[TrackerPayload]], EventSource, 'TrackerConfig'], Any] = None
    on_profile_ready: Callable = None
    on_profile_merge: Callable[[Profile], Profile] = None
    on_flow_ready: Callable = None
    on_result_ready: Callable[[List['TrackerResult'], ConsoleLog], Any] = None
    internal_source: Any = None
    run_async: bool = False
    static_profile_id: bool = False
