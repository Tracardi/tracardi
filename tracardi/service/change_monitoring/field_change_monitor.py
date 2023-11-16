from collections import defaultdict

from typing import List, Any, Optional, Dict
from datetime import datetime

from tracardi.domain.event_source import EventSource
from tracardi.domain.session import Session
from tracardi.service.utils.getters import get_entity_id


class FieldChangeTimestampManager:

    def __init__(self):
        self._log: Dict[str, Dict[str, dict]] = defaultdict(dict)

    def append(self, type: str, session_id:str, source_id:str, field: str, value: Any):
        self._log[type][field]= dict(
                id=field,
                type=type,
                timestamp=str(datetime.utcnow()),
                source_id=source_id,
                session_id=session_id,
                field=field,
                value=value
            )

    def merge(self, timestamps: List[Dict]):
        for timestamp in timestamps:
            self.append(
                type=timestamp['type'],
                session_id=timestamp['session_id'],
                source_id=timestamp['source_id'],
                field=timestamp['field'],
                value=timestamp['value']
            )

    def get_log(self) -> Dict[str, Dict[str, dict]]:
        return self._log

    def get_list(self) -> List[Dict]:
        result = []
        for field_dicts in self._log.values():
            for log_entry in field_dicts.values():
                result.append(log_entry)
        return result


class FieldChangeLogManager:

    def __init__(self):
        self._log: List[dict] = []

    def append(self, type: str, session_id:str, source_id:str, field: str, value: Any):
        self._log.append(
            dict(
                id=field,
                type=type,
                timestamp=str(datetime.utcnow()),
                source_id=source_id,
                session_id=session_id,
                field=field,
                value=value
            )
        )

    def get_log(self) -> List[dict]:
        return self._log

class FieldTimestampMonitor:

    def __init__(self,
                 flat_profile,
                 type: str,
                 session:Optional[Session] = None,
                 source:Optional[EventSource]=None,
                 track_history=True):

        self.source_id = get_entity_id(source)
        self.session_id = get_entity_id(session)
        self.track_history = track_history
        self.type = type
        self.flat_profile = flat_profile
        self._timestamps_log: FieldChangeTimestampManager = FieldChangeTimestampManager()
        self._changes_log: FieldChangeLogManager = FieldChangeLogManager()

    def __contains__(self, item) -> bool:
        return item in self.flat_profile

    def __getitem__(self, item):
        return self.flat_profile[item]

    def __setitem__(self, field: str, value: Any):
        self.flat_profile[field] = value
        self._timestamps_log.append(
            type=self.type,
            session_id=self.session_id,
            source_id=self.source_id,
            field=field,
            value=value
        )
        if self.track_history:
            self._changes_log.append(
                type=self.type,
                field=field,
                session_id=self.session_id,
                source_id=self.source_id,
                value=value
            )

    def get_changed_fields_timestamps(self) -> List[dict]:
        return self._timestamps_log.get_list()

    def get_changed_fields_log(self) -> List[dict]:
        return self._changes_log.get_log()
