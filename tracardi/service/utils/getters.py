from typing import Optional

from tracardi.domain.entity import Entity


def get_entity_id(entity: Optional[Entity]) -> Optional[str]:
    return entity.id if isinstance(entity, Entity) else None
