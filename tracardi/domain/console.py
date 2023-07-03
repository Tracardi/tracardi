from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel
from tracardi.service.secrets import encrypt, decrypt


class Metadata(BaseModel):
    timestamp: datetime = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if 'timestamp' not in data or data['timestamp'] is None:
            self.timestamp = datetime.utcnow()


class ConsoleRecord(BaseModel):
    metadata: Optional[Metadata] = None
    event_id: Optional[str] = None
    flow_id: Optional[str] = None
    node_id: Optional[str] = None
    profile_id: Optional[str] = None
    origin: str
    class_name: str
    module: str
    type: str
    message: str
    traceback: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if 'metadata' not in data or data['metadata'] is None:
            self.metadata = Metadata(timestamp=datetime.utcnow())


class Console(BaseModel):
    metadata: Optional[Metadata] = None
    event_id: Optional[str] = None
    flow_id: Optional[str] = None
    node_id: Optional[str] = None
    profile_id: Optional[str] = None
    origin: str
    class_name: str
    module: str
    type: str
    message: str
    traceback: List[dict] = []

    def __init__(self, **data: Any):
        super().__init__(**data)
        if 'metadata' not in data or data['metadata'] is None:
            self.metadata = Metadata(timestamp=datetime.utcnow())

    def encode_record(self) -> ConsoleRecord:
        data = self.dict()
        data['traceback'] = encrypt(data['traceback'])
        return ConsoleRecord(**data)

    @staticmethod
    def decode_record(data: dict):
        data['traceback'] = decrypt(data['traceback'])
        return Console(**data)
