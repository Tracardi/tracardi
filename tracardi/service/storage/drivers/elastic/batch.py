from tracardi.domain.batch import Batch, BatchRecord
from tracardi.service.storage.factory import storage_manager
from typing import Optional


async def load(id: str) -> Optional[Batch]:
    batch = await storage_manager("batch").load(id)
    if batch is None:
        return None
    batch = BatchRecord(**batch)
    return Batch.decode(batch)


async def add_batch(batch: Batch):
    batch = batch.encode()
    return await storage_manager("batch").upsert(batch.dict())


async def delete(id: str):
    return await storage_manager("batch").delete(id)


async def load_batches(limit: int = 100, query: str = None):
    if query is None:
        return list(await storage_manager("batch").load_all(limit=limit))

    else:
        return [doc["_source"] for doc in (await storage_manager("batch").query({
            "query": {
                "wildcard": {
                    "name": f"{query}*"
                }
            },
            "size": limit
        }))["hits"]["hits"]]


async def refresh():
    return await storage_manager("batch").refresh()
