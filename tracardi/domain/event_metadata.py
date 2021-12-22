from pydantic import BaseModel
from tracardi.domain.time import Time


class EventMetadata(BaseModel):
    time: Time
    ip: str = None
    status: str = None
