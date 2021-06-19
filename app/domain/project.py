from app.domain.entity import Entity
from app.service.storage.collection_crud import CollectionCrud
from app.service.storage.crud import StorageCrud


class Project(Entity):
    name: str

    def storage(self) -> StorageCrud:
        return StorageCrud("project", Project, entity=self)


class Projects(list):

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("project", self)
