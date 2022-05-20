from tracardi.service.storage.factory import storage_manager


def load_all():
    return storage_manager('mapping').load_all()
