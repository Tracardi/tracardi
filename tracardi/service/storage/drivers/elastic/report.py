from tracardi.service.storage.factory import storage_manager
from tracardi.domain.report import Report, ReportRecord
from typing import List


async def load(id: str) -> Report:
    result = await storage_manager("report").load(id)
    return Report.decode(ReportRecord(**result))


async def upsert(report: Report):
    return await storage_manager("report").upsert(report.encode().dict())


async def load_all(start: int = 0, limit: int = 100) -> List[Report]:
    result = await storage_manager("report").load_all(start, limit)
    return [Report.decode(ReportRecord(**record)) for record in result]


async def delete(id: str):
    return await storage_manager("report").delete(id)


async def search_by_name(name: str) -> List[Report]:
    query = {
        "query": {
            "wildcard": {"name": f"*{name}*"}
        }
    }
    result = await storage_manager("report").query(query)
    result = result["hits"]["hits"]
    return [Report.decode(ReportRecord(**record["_source"])) for record in result]
