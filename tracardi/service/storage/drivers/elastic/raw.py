from tracardi.service.storage.factory import storage_manager
from tracardi.service.storage.persistence_service import PersistenceService


def index(idx) -> PersistenceService:
    return storage_manager(idx)
