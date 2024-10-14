# The function to be tested
from typing import Optional

from tracardi.domain.entity import Entity, FlatEntity
from tracardi.service.utils.getters import get_entity_id


# Pytest cases
def test_get_entity_id_with_entity():
    entity = Entity(id="entity_123")
    assert get_entity_id(entity) == "entity_123"


def test_get_entity_id_with_flat_entity():
    flat_entity = FlatEntity(dict(id="flat_entity_456"))
    assert get_entity_id(flat_entity) == "flat_entity_456"


def test_get_entity_id_with_none():
    assert get_entity_id(None) is None


def test_get_entity_id_with_invalid_type():
    class AnotherClass:
        def __init__(self, entity_id: str):
            self.id = entity_id

    another_instance = AnotherClass("another_789")
    assert get_entity_id(another_instance) is None


def test_get_entity_id_with_missing_id():
    class EntityNoId:
        pass

    entity_no_id = EntityNoId()
    assert get_entity_id(entity_no_id) is None
