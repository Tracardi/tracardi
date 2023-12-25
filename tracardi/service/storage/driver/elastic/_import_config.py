from tracardi.domain.import_config import ImportConfig, ImportConfigRecord
from tracardi.service.storage.factory import storage_manager
from typing import Optional


# async def load(id: str) -> Optional[ImportConfig]:
#     import_configuration = await storage_manager("import").load(id)
#     if import_configuration is None:
#         return None
#     import_configuration = ImportConfigRecord(**import_configuration)
#     return ImportConfig.decode(import_configuration)


# async def save(batch: ImportConfig):
#     batch = batch.encode()
#     return await storage_manager("import").upsert(batch)


# async def delete(id: str):
#     sm = storage_manager("import")
#     return await sm.delete(id, index=sm.get_single_storage_index())


# async def load_all(limit: int = 100, query: str = None):
#     if query is None:
#         result = await storage_manager("import").load_all(limit=limit)
#     else:
#         result = await storage_manager("import").query({
#             "query": {
#                 "wildcard": {
#                     "name": f"*{query}*"
#                 }
#             },
#             "size": limit
#         })
#
#     return list(result)


# async def refresh():
#     return await storage_manager("import").refresh()
