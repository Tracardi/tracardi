from tracardi.domain.entity import Entity
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.service.storage.collection_crud import CollectionCrud
from tracardi.service.storage.crud import StorageCrud


class Project(Entity):
    name: str

    def storage(self) -> StorageCrud:
        return StorageCrud("project", Project, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'project',
            Project
        )


class Projects(list):

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("project", self)
