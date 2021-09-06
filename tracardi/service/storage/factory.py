from tracardi.domain.entity import Entity
from tracardi.service.storage.crud import StorageCrud


def storage(instance: Entity) -> StorageCrud:
    storage_info = instance.storage_info()
    return StorageCrud(
        storage_info.index,
        storage_info.domain_class_ref,
        entity=instance,
        exclude=storage_info.exclude,
        exclude_unset=storage_info.exclude_unset
    )
