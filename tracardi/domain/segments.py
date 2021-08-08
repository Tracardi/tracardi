from tracardi.event_server.service.persistence_service import PersistenceService
from tracardi.service.storage.collection_crud import CollectionCrud
from tracardi.service.storage.elastic_storage import ElasticStorage


class Segments(list):

    # Persistence
    def bulk(self) -> CollectionCrud:
        return CollectionCrud("segment", self)

    @staticmethod
    def storage() -> PersistenceService:
        return PersistenceService(ElasticStorage(index_key="segment"))
