from datetime import datetime

import time
from typing import Optional, Any, List
from pydantic import BaseModel


class FieldChange(BaseModel):
    field: str
    value: Optional[Any] = None
    event_type: Optional[str] = None
    ts: Optional[float] = None

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if self.ts is None:
            self.ts = time.time()

    def __repr__(self):
        return f"{super().__repr__()} +{datetime.fromtimestamp(self.ts)}"

class ProfileFieldChanges(BaseModel):
    entity: str
    session_id: Optional[str] = None
    changes: Optional[List[FieldChange]] = []

    def has_changes(self) -> bool:
        return bool(self.changes)

    def get_as_list(self) -> List[dict]:
        return [item.model_dump() for item in self.changes]

    def has_change_in_field(self, fields: List[str]) -> Optional[FieldChange]:
        for change in self.changes:
            if change.field in fields:
                return change

        return None


class ListOfProfileChanges(List[ProfileFieldChanges]):

    def has_change_in_field(self, fields: List[str]) -> Optional[FieldChange]:
        for item in self:
            changed_field = item.has_change_in_field(fields)
            if changed_field is not None:
                return changed_field
        return None

    def serialize(self) -> List[dict]:
        return [item.model_dump(mode="json") for item in self]