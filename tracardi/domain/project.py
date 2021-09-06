from tracardi.domain.entity import Entity
from tracardi.domain.value_object.storage_info import StorageInfo


class Project(Entity):
    name: str

    # def storage(self) -> StorageCrud:
    #     return StorageCrud("project", Project, entity=self)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'project',
            Project
        )
