from typing import Optional, Any, List
from pydantic import BaseModel


class FieldChange(BaseModel):
    field: str
    value: Optional[Any] = None

class ProfileFieldChanges(BaseModel):
    entity: str
    session_id: Optional[str] = None
    event_type: Optional[str] = None
    changes: List[FieldChange]
