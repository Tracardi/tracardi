from datetime import datetime
from typing import List, Optional, Any

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.time import Time


class EventProcessors(BaseModel):
    rules: List[str] = []
    third_party: List[str] = []


class EventTime(BaseModel):
    insert: Optional[datetime]
    process_time: float = None

    def __init__(self, **data: Any):
        if 'insert' not in data:
            data['insert'] = datetime.utcnow()
        super().__init__(**data)


class EventMetadata(BaseModel):
    time: EventTime
    ip: str = None
    status: str = None
    processed_by: EventProcessors = EventProcessors()
    profile_less: bool = False
    debug: bool = False
    valid: bool = True
    error: bool = False
    warning: bool = False
    instance: Optional[Entity] = None


class EventPayloadMetadata(BaseModel):
    time: Time
    ip: str = None
    status: str = None
