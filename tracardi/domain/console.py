from datetime import datetime
from typing import Any, List
from pydantic import BaseModel
from tracardi.service.secrets import encrypt, decrypt


class Metadata(BaseModel):
    timestamp: datetime = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.timestamp = datetime.utcnow()


class ConsoleRecord(BaseModel):
    metadata: Metadata = Metadata()
    event_id: str = None
    flow_id: str = None
    profile_id: str = None
    origin: str
    class_name: str
    module: str
    type: str
    message: str
    traceback: str = None


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
    traceback: List[dict] = []

    def encode_record(self) -> ConsoleRecord:
        data = self.dict()
        data['traceback'] = encrypt(data['traceback'])
        return ConsoleRecord(**data)

    @staticmethod
    def decode_record(data: dict):
        data['traceback'] = decrypt(data['traceback'])
        return Console(**data)
