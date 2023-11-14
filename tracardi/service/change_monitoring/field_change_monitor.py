from uuid import uuid4
from typing import List, Any
from datetime import datetime


class FieldChangeMonitor:

    def __init__(self, flat_profile, type, track_history=True):
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
                timestamp=datetime.utcnow(),
                field=field,
                value=value
            )
        )
        if self.track_history:
            self._changes.append(
                dict(
                    id=str(uuid4()),
                    type=self.type,
                    timestamp=datetime.utcnow(),
                    field=field,
                    value=value
                )
            )

    def get_changed_values(self) -> List[dict]:
        return self._changes
