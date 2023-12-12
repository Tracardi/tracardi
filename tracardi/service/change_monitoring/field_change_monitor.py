from collections import defaultdict
from tracardi.service.utils.date import now_in_utc

from uuid import uuid4

from typing import List, Any, Optional, Dict

from tracardi.domain.event_source import EventSource
from tracardi.domain.session import Session
from tracardi.service.utils.getters import get_entity_id


class FieldChangeTimestampManager:

    def __init__(self):
        self._log: Dict[str, Dict[str, dict]] = defaultdict(dict)

    def append(self, type: str, profile_id:str, event_id:str, session_id:str, source_id:str, field: str, value: Any):
        self._log[type][field]= dict(
                id=f"{field}:{profile_id}",
                type=type,
                timestamp=str(now_in_utc()),
                profile_id=profile_id,
                event_id=event_id,
                source_id=source_id,
                session_id=session_id,
                field=field,
                value=value
            )

    def merge(self, timestamps: List[Dict]):
        for timestamp in timestamps:
            self.append(
                type=timestamp['type'],
                profile_id=timestamp['profile_id'],
                event_id=timestamp['event_id'],
                session_id=timestamp['session_id'],
                source_id=timestamp['source_id'],
                field=timestamp['field'],
                value=timestamp['value']
            )

    def has_changes(self):
        return bool(self._log)

    def get_log(self) -> Dict[str, Dict[str, dict]]:
        return self._log

    def get_list(self) -> List[Dict]:
        result = []
        for field_dicts in self._log.values():
            for log_entry in field_dicts.values():
                result.append(log_entry)
        return result

    def get_history_log(self) -> List[Dict]:
        result = []
        for field_dicts in self._log.values():
            for log_entry in field_dicts.values():
                log_entry['id'] = str(uuid4())
                result.append(log_entry)
        return result

    def get_timestamps(self):
        for field_dicts in self._log.values():
            for log_entry in field_dicts.values():
                yield log_entry['field'], [log_entry['timestamp'], log_entry['event_id']]


class FieldChangeLogManager:

    def __init__(self):
        self._log: List[dict] = []

    def append(self, type: str, profile_id:str, event_id: str, session_id:str, source_id:str, field: str, value: Any):
        self._log.append(
            dict(
                id=str(uuid4()),
                type=type,
                timestamp=str(now_in_utc()),
                profile_id=profile_id,
                event_id=event_id,
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
                 profile_id: str,
                 event_id: str,
                 session:Optional[Session] = None,
                 source:Optional[EventSource]=None):

        self.event_id = event_id
        self.profile_id = profile_id
        self.source_id = get_entity_id(source)
        self.session_id = get_entity_id(session)
        self.type = type
        self.flat_profile = flat_profile
        self._timestamps_log: FieldChangeTimestampManager = FieldChangeTimestampManager()

    def __contains__(self, item) -> bool:
        return item in self.flat_profile

    def __getitem__(self, item):
        return self.flat_profile[item]

    def __setitem__(self, field: str, value: Any):
        self.flat_profile[field] = value
        self._timestamps_log.append(
            type=self.type,
            profile_id=self.profile_id,
            event_id=self.event_id,
            session_id=self.session_id,
            source_id=self.source_id,
            field=field,
            value=value
        )

    def get_timestamps_log(self) -> FieldChangeTimestampManager:
        return self._timestamps_log

    def get_timestamps_list(self) -> List[dict]:
        return self._timestamps_log.get_list()


    def get_timestamps(self):
        return self._timestamps_log.get_timestamps()
