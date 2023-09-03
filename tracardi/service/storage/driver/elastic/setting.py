from tracardi.domain.setting import Setting
from tracardi.service.storage.factory import storage_manager
from typing import List, Optional
from tracardi.domain.storage_record import StorageRecords


async def load(type: str, id: str) -> Optional[Setting]:
    result = await storage_manager("setting").load(id)
    if result is not None:
        setting = Setting(**result)
        if type != setting.type:
            raise TypeError(f"Settings with id {id} is not of type {type}. Expected {type}, got {setting.type}")
        return setting
    return None


async def upsert(setting: Setting):
    return await storage_manager("setting").upsert(setting)


async def save_all(settings: List[Setting]):
    return await storage_manager("setting").upsert(settings)


async def load_all(type: str, start: int = 0, limit: int = 100) -> List[Setting]:
    query = {
        "from": start,
        "size": limit,
        "query": {
            "term": {
                "type": type
            }
        }
    }

    result = await storage_manager("setting").query(query)
    return [Setting(**record) for record in result]


async def delete(id: str):
    sm = storage_manager("setting")
    return await sm.delete(id, index=sm.get_single_storage_index())


async def refresh():
    return await storage_manager("setting").refresh()


async def flush():
    return await storage_manager("setting").flush()


async def search_by_name(type: str, name: str) -> List[Setting]:
    query = {
        "query": {
            "wildcard": {"name": f"*{name}*"}
        }
    }
    result = await storage_manager("setting").query(query)
    return [Setting(**record) for record in result]


async def load_for_grouping(type: str, name: Optional[str] = None) -> StorageRecords:
    query = {
        "query": {
            "wildcard": {"name": f"*{name if name is not None else ''}*"}
        }
    }
    result = await storage_manager("setting").query(query)
    result.transform_hits(lambda hit: Setting(**hit).model_dict())
    return result


async def query(query: dict) -> List[Setting]:
    result = await storage_manager("setting").query(query)
    return [Setting(**record) for record in result]
