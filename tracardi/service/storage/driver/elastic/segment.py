from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager


async def load_by_id(id: str):
    return await storage_manager("segment").load(id)


async def delete_by_id(id: str):
    sm = storage_manager('segment')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def load_segments(event_type, limit=500) -> StorageRecords:
    return await storage_manager(index="segment"). \
        load_by_query_string("(NOT _exists_:eventType) OR eventType: \"{}\"".format(event_type, limit))


async def load_all(start: int = 0, limit: int = 100) -> StorageRecords:
    return await storage_manager('segment').load_all(start, limit)


async def load_by_name(name, limit=50) -> StorageRecords:
    return await storage_manager(index="segment"). \
        load_by_query_string(f"name: \"{name}*\"", limit=limit)


async def refresh():
    return await storage_manager('segment').refresh()


async def flush():
    return await storage_manager('segment').flush()


async def save(data: dict):
    return await storage_manager('segment').upsert(data)
