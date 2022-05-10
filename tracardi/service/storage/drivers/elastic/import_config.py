from tracardi.domain.import_config import ImportConfig, ImportConfigRecord
from tracardi.service.storage.factory import storage_manager
from typing import Optional


async def load(id: str) -> Optional[ImportConfig]:
    batch = await storage_manager("import").load(id)
    if batch is None:
        return None
    batch = ImportConfigRecord(**batch)
    return ImportConfig.decode(batch)


async def save(batch: ImportConfig):
    batch = batch.encode()
    return await storage_manager("import").upsert(batch.dict())


async def delete(id: str):
    return await storage_manager("import").delete(id)


async def load_all(limit: int = 100, query: str = None):
    if query is None:
        return list(await storage_manager("import").load_all(limit=limit))

    else:
        return [doc["_source"] for doc in (await storage_manager("import").query({
            "query": {
                "wildcard": {
                    "name": f"{query}*"
                }
            },
            "size": limit
        }))["hits"]["hits"]]


async def refresh():
    return await storage_manager("import").refresh()
