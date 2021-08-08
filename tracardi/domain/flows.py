import logging

from tracardi.event_server.service.persistence_service import PersistenceService
from tracardi.service.storage.collection_crud import CollectionCrud
from tracardi.service.storage.elastic_storage import ElasticStorage


rules_logger = logging.getLogger('Flows')


class Flows(list):

    def storage(self) -> PersistenceService:
        return PersistenceService(ElasticStorage(index_key="flow"))

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("flow", self)

