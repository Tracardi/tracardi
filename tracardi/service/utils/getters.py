import os

from typing import Optional

from tracardi.domain.entity import Entity


def get_entity_id(entity: Optional[Entity]) -> Optional[str]:
    return entity.id if isinstance(entity, Entity) else None


def get_entity(entity: Optional[Entity]) -> Optional[Entity]:
    return Entity(id=entity.id) if isinstance(entity, Entity) else None


def get_env_as_int(env_key, default_value):
    value = os.environ.get(env_key, default_value)
    if not value:
        return default_value
    return int(value)
