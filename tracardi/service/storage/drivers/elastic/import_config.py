from tracardi.domain.import_config import ImportConfig, ImportConfigRecord
from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.factory import storage_manager
from typing import Optional


async def load(id: str) -> Optional[ImportConfig]:
    import_configuration = await storage_manager("import").load(id)
    if import_configuration is None:
        return None
    import_configuration = ImportConfigRecord(**import_configuration)
    return ImportConfig.decode(import_configuration)


async def save(batch: ImportConfig):
    batch = batch.encode()
    return await storage_manager("import").upsert(batch.dict())


async def delete(id: str):
    return await storage_manager("import").delete(id)


async def load_all(limit: int = 100, query: str = None):
    if query is None:
        result = await storage_manager("import").load_all(limit=limit)
    else:
        result = StorageResult(await storage_manager("import").query({
            "query": {
                "wildcard": {
                    "name": f"*{query}*"
                }
            },
            "size": limit
        }))

    return list(result)


async def refresh():
    return await storage_manager("import").refresh()
