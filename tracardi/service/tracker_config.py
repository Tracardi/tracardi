from typing import List, Callable, Any, Type
from pydantic import BaseModel
from tracardi.domain.profile import Profile
from tracardi.service.console_log import ConsoleLog


class TrackerConfig(BaseModel):
    ip: str
    allowed_bridges: List[str]
    on_source_ready: Type = None
    on_profile_ready: Callable = None
    on_profile_merge: Callable[[Profile], Profile] = None
    on_flow_ready: Callable = None
    on_result_ready: Callable[[List['TrackerResult'], ConsoleLog], Any] = None
    internal_source: Any = None
    run_async: bool = False
    static_profile_id: bool = False
