from typing import Optional, List, Set

from tracardi.domain.entity import Entity


class SystemEntityProperty(Entity):
    entity: str
    property: str
    type: str
    default: Optional[str] = None
    optional: bool = False
    converter: Optional[str] = None
    merge_strategies: Optional[List[str]]
    nested: Optional[bool] = False
    undefined: Optional[bool] = False


class SystemEntityPropertySet(Set[SystemEntityProperty]):

    def __str__(self):
        return f"SystemEntityPropertySet({[item.property for item in self]})"
