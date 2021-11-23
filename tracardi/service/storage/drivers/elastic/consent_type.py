from tracardi.service.storage.factory import storage_manager
from uuid import UUID


async def add_consent(id: UUID, name: str, description: str, revokable: bool, default_value: str):
    return await storage_manager("consent-type").upsert(data={
        "id": id,
        "name": name,
        "description": description,
        "revokable": revokable,
        "default_value": default_value
    })


async def delete_by_id(consent_id):
    return await storage_manager("consent-type").delete(consent_id)


async def load(start: int = 0, limit: int = 10):
    return await storage_manager("consent-type").load_all(start=start, limit=limit)
