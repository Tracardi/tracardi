from datetime import datetime
from typing import Optional
from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext


class WorkflowSegmentationTrigger(NamedEntityInContext):
    timestamp: Optional[datetime] = None
    description: Optional[str] = ""
    enabled: bool = True
    workflow: NamedEntity
    type: Optional[str] = 'workflow'

    operation: Optional[str] = None
    condition: Optional[str] = None
    segment: Optional[str] = None
    code: Optional[str] = None