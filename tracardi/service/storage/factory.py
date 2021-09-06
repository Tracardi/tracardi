import elasticsearch
from typing import Union
from tracardi.service.storage.elastic_storage import ElasticStorage
from tracardi.service.storage.persistence_service import PersistenceService
from tracardi.domain.entity import Entity
from pydantic import BaseModel
from tracardi.domain.agg_result import AggResult
from tracardi.exceptions.exception import TracardiException, StorageException
from tracardi.domain.storage_result import StorageResult
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
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
        return storage(self.index)


class EntityStorageCrud(BaseStorageCrud):

    async def load(self, domain_class_ref=None):
        service = self._get_storage_service()
        data = await service.load(self.entity.id)

        if data:
            if domain_class_ref is None:
                return domain.Entity(**data)
            return domain_class_ref(**data)

        return None

    async def load_by(self, field: str, value: str, limit: int = 100) -> StorageResult:
        service = self._get_storage_service()
        return await service.load_by(field, value, limit)

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


class CollectionCrud:

    def __init__(self, index, payload):
        self.payload = payload
        self.index = index
        self.storage = storage(self.index)

    async def save(self) -> BulkInsertResult:
        try:
            if not isinstance(self.payload, list):
                raise TracardiException("CollectionCrud dave payload must be list.")
            data = [p.dict() for p in self.payload if isinstance(p, BaseModel)]
            return await self.storage.upsert(data)

        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def load(self) -> StorageResult:
        try:

            return await self.storage.load_all()

        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))

    async def uniq_field_value(self, field) -> AggResult:
        try:
            query = {
                "size": "0",
                "aggs": {
                    "uniq": {
                        "terms": {
                            "field": field
                        }
                    }
                }
            }
            return AggResult('uniq', await self.storage.query(query), return_counts=False)
        except elasticsearch.exceptions.ElasticsearchException as e:
            raise StorageException(str(e))


class StorageFor:

    def __init__(self, instance: Entity):
        self.instance = instance
        self.storage_info = instance.storage_info()

    @staticmethod
    def crud(index, class_type):
        return EntityStorageCrud(index, class_type)

    def index(self, index=None) -> Union[EntityStorageCrud, StorageCrud]:
        if self.storage_info is None:
            if index is None:
                raise ValueError("When loading entity of type `{}` you must provide index of that entity.".format(
                    type(self.instance)
                ))
            return EntityStorageCrud(index, entity=self.instance)
        else:
            return StorageCrud(
                self.storage_info.index,
                self.storage_info.domain_class_ref,
                entity=self.instance,
                exclude=self.storage_info.exclude,
                exclude_unset=self.storage_info.exclude_unset
            )


class StorageForBulk:

    def __init__(self, list_of_objects=None):
        if list_of_objects is None:
            list_of_objects = []
        self.collection = list_of_objects

    def index(self, index) -> CollectionCrud:
        return CollectionCrud(index, self.collection)


def storage(index) -> PersistenceService:
    return PersistenceService(ElasticStorage(index_key=index))
