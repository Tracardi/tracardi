from tracardi.domain.storage_result import StorageResult
from tracardi.event_server.service.persistence_service import PersistenceService
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.elastic_storage import ElasticStorage
import tracardi.domain.entity as domain


class BaseStorageCrud:

    def __init__(self, index, entity, exclude=None, exclude_unset=False):
        self.exclude_unset = exclude_unset
        self.exclude = exclude
        self.index = index
        self.entity = entity

    async def delete(self) -> dict:
        service = self._get_storage_service()
        return await service.delete(self.entity.id)

    def _get_storage_service(self):
        return PersistenceService(ElasticStorage(index_key=self.index))


class EntityStorageCrud(BaseStorageCrud):

    async def load(self, domain_class_ref=None):
        service = self._get_storage_service()
        data = await service.load(self.entity.id)

        if data:
            if domain_class_ref is None:
                return domain.Entity(**data)
            return domain_class_ref(**data)

        return None

    async def load_by(self, field, value) -> StorageResult:
        service = self._get_storage_service()
        return await service.load_by(field, value)

    async def delete_by(self, field, value) -> dict:
        service = self._get_storage_service()
        return await service.delete_by(field, value)

    async def save(self, row=None):
        if row is None:
            row = {}
        row['id'] = self.entity.id
        service = self._get_storage_service()
        return await service.upsert(row)


class StorageCrud(BaseStorageCrud):

    def __init__(self, index, domain_class_ref, entity, exclude=None, exclude_unset=False):
        super().__init__(index, entity, exclude, exclude_unset)
        self.domain_class_ref = domain_class_ref

    async def load(self):
        service = self._get_storage_service()
        data = await service.load(self.entity.id)

        if data:
            return self.domain_class_ref(**data)

        return None

    async def save(self) -> BulkInsertResult:
        service = self._get_storage_service()
        return await service.upsert(self.entity.dict(exclude_unset=self.exclude_unset, exclude=self.exclude))
