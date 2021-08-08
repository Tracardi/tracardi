import logging
from tracardi.event_server.service.persistence_service import PersistenceService
from tracardi.service.storage.collection_crud import CollectionCrud
from tracardi.service.storage.elastic_storage import ElasticStorage


_logger = logging.getLogger('FlowActionPlugins')


class FlowActionPlugins(list):

    def storage(self) -> PersistenceService:
        return PersistenceService(ElasticStorage(index_key="action"))

    def bulk(self) -> CollectionCrud:
        return CollectionCrud("action", self)
