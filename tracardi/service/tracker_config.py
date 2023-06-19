from typing import List, Any
from pydantic import BaseModel


class TrackerConfig(BaseModel):
    ip: str
    allowed_bridges: List[str]
    internal_source: Any = None
    run_async: bool = False
    static_profile_id: bool = False
