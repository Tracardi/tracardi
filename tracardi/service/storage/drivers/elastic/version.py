from tracardi.service.storage.factory import storage_manager


def load():
    return storage_manager('version').load(id="0")


def save(version: dict):
    return storage_manager('version').upsert(version, replace_id=True)
