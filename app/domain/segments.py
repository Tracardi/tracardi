from app.event_server.service.persistence_service import PersistenceService
from app.service.storage.collection_crud import CollectionCrud
from app.service.storage.elastic_storage import ElasticStorage


class Segments(list):

    # Persistence
    def bulk(self) -> CollectionCrud:
        return CollectionCrud("segment", self)

    @staticmethod
    def storage() -> PersistenceService:
        return PersistenceService(ElasticStorage(index_key="segment"))
