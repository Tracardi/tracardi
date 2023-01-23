from typing import List, Optional, Union

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.time import EventTime, Time


class EventProcessors(BaseModel):
    rules: List[str] = []
    third_party: List[str] = []


class EventMetadata(BaseModel):
    time: EventTime
    ip: str = None
    status: str = None
    channel: Optional[str] = None
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
