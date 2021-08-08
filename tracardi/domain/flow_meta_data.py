from typing import List, Optional

from tracardi.domain.named_entity import NamedEntity


class FlowMetaData(NamedEntity):
    description: str
    enabled: bool = True
    projects: Optional[List[str]] = ["General"]
