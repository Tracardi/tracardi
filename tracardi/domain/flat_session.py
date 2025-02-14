from datetime import datetime

import uuid

from typing import Optional

from tracardi.common.time.date import now_in_utc
from tracardi.domain.entity import FlatEntity
from tracardi.domain.time import Time
from system.adapter.os.bigdata.elastic.model.storage_record import StorageRecord


class FlatSession(FlatEntity):

    def __init__(self, dictionary):
        super().__init__(dictionary)

    @staticmethod
    def new(id: Optional[str] = None, profile_id: str = None) -> 'FlatSession':
        time = Time()
        time_dict = time.model_dump(mode='json')
        time_dict["timestamp"] = datetime.timestamp(now_in_utc())
        time_dict["duration"] = 0
        time_dict["weekday"] = time.insert.weekday()

        flat_session = FlatSession(dict(
            id=str(uuid.uuid4()) if not id else id,
            metadata={
                "time": time_dict,
                "channel": None,
                "aux": {},
                "status": None
            }
        )

        )

        flat_session.set_new()
        if profile_id is not None:
            flat_session['profile'] = dict(id=profile_id)

        return flat_session

    def is_new(self) -> bool:
        return bool(self.get('operation.new', False))

    def set_new(self, flag=True):
        self.set('operation.new', flag)

    def set_updated(self, flag=True):
        self.set('operation.update', flag)

    @staticmethod
    def from_es_storage_record(record: StorageRecord) -> 'FlatSession':
        fs = FlatSession(dict(record))
        fs.set_new(False)
        fs.set_updated(False)
        fs.set_meta_data(record.get_meta_data())
        return fs
