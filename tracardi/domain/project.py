from tracardi.domain.entity import Entity
from tracardi.service.storage.collection_crud import CollectionCrud
from tracardi.service.storage.crud import StorageCrud


class Project(Entity):
    name: str

    def storage(self) -> StorageCrud:
        return StorageCrud("project", Project, entity=self)


class Projects(list):

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("project", self)
