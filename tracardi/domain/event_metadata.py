from typing import List, Optional

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.time import EventTime, Time


class EventProcessors(BaseModel):
    rules: List[str] = []
    flows: List[str] = []
    third_party: List[str] = []


class EventMetadata(BaseModel):
    aux: Optional[dict] = {}
    time: EventTime
    ip: Optional[str] = None
    status: Optional[str] = 'collected'
    channel: Optional[str] = None
    processed_by: EventProcessors = EventProcessors()
    profile_less: Optional[bool] = False
    debug: Optional[bool] = False
    valid: Optional[bool] = True
    error: Optional[bool] = False
    warning: Optional[bool] = False
    merge: Optional[bool] = False
    instance: Optional[Entity] = None


class EventPayloadMetadata(BaseModel):
    time: Time
    ip: Optional[str] = None
    status: Optional[str] = None
