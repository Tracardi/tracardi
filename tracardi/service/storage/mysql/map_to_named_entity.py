from tracardi.domain.named_entity import NamedEntity


def map_to_named_entity(table) -> NamedEntity:
    return NamedEntity(
        id=table.id,
        name=table.name,
    )