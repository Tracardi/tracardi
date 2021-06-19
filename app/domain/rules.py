import logging
from app.event_server.service.persistence_service import PersistenceService
from app.service.storage.elastic_storage import ElasticStorage


rules_logger = logging.getLogger('Rules')


class Rules(list):

    def storage(self) -> PersistenceService:
        return PersistenceService(ElasticStorage(index_key="rule"))
