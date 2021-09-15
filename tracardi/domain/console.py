from datetime import datetime
from typing import Any
from pydantic import BaseModel


class Metadata(BaseModel):
    timestamp: datetime = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.timestamp = datetime.utcnow()


class Console(BaseModel):
    metadata: Metadata = Metadata()
    event_id: str = None
    flow_id: str = None
    profile_id: str = None
    origin: str
    class_name: str
    module: str
    type: str
    message: str

    # todo cross field validation
