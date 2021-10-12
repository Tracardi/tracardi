from uuid import uuid4

from time import time

from tracardi.service.network import local_ip
from tracardi.service.singleton import Singleton
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.domain.entity import Entity
from datetime import datetime


class ApiInstanceRecord(Entity):
    ip: str = None
    timestamp: datetime = datetime.utcnow()
    all_track_requests: int = 0
    track_requests: int = 0
    track_rps: float = 0

    # Persistence

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'api-instance',
            ApiInstance
        )


class ApiInstance(metaclass=Singleton):
    def __init__(self):
        self.record = ApiInstanceRecord(
            id=str(uuid4()),
            ip=local_ip
        )
        self._start_time = time()

    def get_record(self) -> ApiInstanceRecord:
        passed_time = time() - self._start_time
        self.record.track_rps = (self.record.track_requests / passed_time) if passed_time > 0 \
            else self.record.track_requests/0.000001
        return self.record

    def reset(self):
        self.record.track_requests = 0
        self._start_time = time()

    def increase_track_requests(self):
        self.record.all_track_requests += 1
        self.record.track_requests += 1
