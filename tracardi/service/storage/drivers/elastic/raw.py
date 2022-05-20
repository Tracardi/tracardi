from typing import List

from tracardi.domain.entity import Entity
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


async def aliases():
    es = ElasticClient.instance()
    return await es.list_aliases()


async def clone(source_index, destination_index):
    es = ElasticClient.instance()
    return await es.clone(source_index, destination_index)


async def exists_index(index):
    es = ElasticClient.instance()
    return await es.exists_index(index)


async def exists_alias(alias, index):
    es = ElasticClient.instance()
    return await es.exists_alias(alias, index=index)


async def create_alias(index, alias):
    es = ElasticClient.instance()
    return await es.create_alias(index, alias)


async def refresh(index):
    es = ElasticClient.instance()
    return await es.refresh(index)
