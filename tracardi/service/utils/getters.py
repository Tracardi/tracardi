from typing import Optional

from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.profile import FlatProfile


def get_entity_id(entity: Optional[Entity]) -> Optional[str]:
    return entity.id if isinstance(entity, Entity) else None


def get_entity(entity: Optional[Entity]) -> Optional[Entity]:
    return Entity(id=entity.id) if isinstance(entity, Entity) else None


def get_primary_entity(entity: Optional[PrimaryEntity]) -> Optional[PrimaryEntity]:
    return PrimaryEntity(id=entity.id, primary_id=entity.primary_id) if isinstance(entity, PrimaryEntity) else None


def get_primary_entity_from_flat_profile(flat_profile: Optional[FlatProfile]) -> Optional[PrimaryEntity]:
    if flat_profile and 'id' not in flat_profile:
        return PrimaryEntity(id=flat_profile['id'], primary_id=flat_profile['primary_id'])
    return None
