from typing import List

from pydantic import BaseModel
from tracardi.domain.time import Time


class EventProcessors(BaseModel):
    rules: List[str] = []
    third_party: List[str] = []


class EventMetadata(BaseModel):
    time: Time
    ip: str = None
    status: str = None
    processed_by: EventProcessors = EventProcessors()
    profile_less: bool = False


class EventPayloadMetadata(BaseModel):
    time: Time
    ip: str = None
    status: str = None
