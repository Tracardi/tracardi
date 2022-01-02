from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.factory import storage_manager


async def get_by_id(consent_id):
    return await storage_manager("consent-type").load(consent_id)


async def add_consent(id: str, name: str, description: str, revokable: bool, default_value: str, enabled: bool):
    return await storage_manager("consent-type").upsert(data={
        "id": id,
        "name": name,
        "description": description,
        "revokable": revokable,
        "default_value": default_value,
        "enabled": enabled
    })


async def delete_by_id(consent_id):
    return await storage_manager("consent-type").delete(consent_id)


async def load_all(start: int = 0, limit: int = 10) -> StorageResult:
    return await storage_manager("consent-type").load_all(start=start, limit=limit)


async def load_all_active(limit: int = 100) -> StorageResult:
    return await storage_manager("consent-type").load_by('enabled', True, limit=limit)


async def refresh():
    return await storage_manager('consent-type').refresh()


async def flush():
    return await storage_manager('consent-type').flush()
