from tracardi.service.storage.factory import storage_manager


async def load_all(start: int = 0, limit: int = 100):
    return await storage_manager('log').load_all(
        start,
        limit,
        sort=[{"date": {"order": "desc", "format": "strict_date_optional_time_nanos"}}])
