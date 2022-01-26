from typing import List

from tracardi.domain.entity import Entity
from tracardi.domain.value_object.storage_info import StorageInfo
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.factory import storage_manager, StorageFor, StorageCrud, StorageForBulk, CollectionCrud
from tracardi.service.storage.persistence_service import PersistenceService


def index(idx) -> PersistenceService:
    return storage_manager(idx)


def entity(entity: Entity) -> StorageCrud:
    return StorageFor(entity).index()


def collection(index, dataset: List) -> CollectionCrud:
    return StorageForBulk(dataset).index(index)


def load(id: str, index, output):
    return StorageFor(Entity(id=id)).index(index).load(output)


async def indices():
    es = ElasticClient.instance()
    return await es.list_indices()
