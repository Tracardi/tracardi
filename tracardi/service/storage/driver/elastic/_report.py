# from tracardi.service.storage.factory import storage_manager
# from tracardi.domain.report import Report, ReportRecord
# from typing import List, Optional
# from tracardi.domain.storage_record import StorageRecords


# async def load(id: str) -> Optional[Report]:
#     result = await storage_manager("report").load(id)
#     if result is not None:
#         return Report.decode(ReportRecord(**result))
#     return None


# async def upsert(report: Report):
#     return await storage_manager("report").upsert(report.encode())


# async def load_all(start: int = 0, limit: int = 100) -> List[Report]:
#     result = await storage_manager("report").load_all(start, limit)
#     return [Report.decode(ReportRecord(**record)) for record in result]


# async def delete(id: str):
#     sm = storage_manager("report")
#     return await sm.delete(id, index=sm.get_single_storage_index())


# async def refresh():
#     return await storage_manager("report").refresh()


# async def flush():
#     return await storage_manager("report").flush()


# async def search_by_name(name: str) -> List[Report]:
#     query = {
#         "query": {
#             "wildcard": {"name": f"*{name}*"}
#         }
#     }
#     result = await storage_manager("report").query(query)
#     return [Report.decode(ReportRecord(**record)) for record in result]


# async def load_for_grouping(name: Optional[str] = None) -> StorageRecords:
#     query = {
#         "query": {
#             "wildcard": {"name": f"*{name if name is not None else ''}*"}
#         }
#     }
#     result = await storage_manager("report").query(query)
#     result.transform_hits(lambda hit: Report.decode(ReportRecord(**hit)).model_dump())
#     return result
