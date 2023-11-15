from uuid import uuid4
from typing import List, Any, Optional
from datetime import datetime

from tracardi.domain.event_source import EventSource
from tracardi.domain.session import Session
from tracardi.service.utils.getters import get_entity_id


class FieldChangeMonitor:

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
        self._changes: List[dict] = []

    def __contains__(self, item) -> bool:
        return item in self.flat_profile

    def __getitem__(self, item):
        return self.flat_profile[item]

    def __setitem__(self, field: str, value: Any):
        self.flat_profile[field] = value
        self._changes.append(
            dict(
                id=field,
                type=self.type,
                timestamp=str(datetime.utcnow()),
                source_id=self.source_id,
                session_id=self.session_id,
                field=field,
                value=value
            )
        )
        if self.track_history:
            self._changes.append(
                dict(
                    id=str(uuid4()),
                    type=self.type,
                    timestamp=str(datetime.utcnow()),
                    source_id=self.source_id,
                    session_id=self.session_id,
                    field=field,
                    value=value
                )
            )

    def get_changed_values(self) -> List[dict]:
        return self._changes
