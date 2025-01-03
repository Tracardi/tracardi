from typing import Optional, Union

from tracardi.domain.entity import Entity, PrimaryEntity, FlatEntity


def get_entity_id(entity: Union[Optional[Entity],Optional[FlatEntity]]) -> Optional[str]:
    return entity.id if isinstance(entity, (Entity, FlatEntity)) else None


def get_entity(entity: Optional[Entity]) -> Optional[Entity]:
    return Entity(id=entity.id) if isinstance(entity, Entity) else None


def get_primary_entity(entity: Optional[PrimaryEntity]) -> Optional[PrimaryEntity]:
    return PrimaryEntity(id=entity.id, primary_id=entity.primary_id) if isinstance(entity, PrimaryEntity) else None

