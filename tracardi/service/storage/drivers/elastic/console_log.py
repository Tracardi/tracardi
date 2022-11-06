from typing import List, Dict

from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.factory import storage_manager


async def load_by_flow(flow_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> StorageRecords:
    return await storage_manager('console-log').load_by("flow_id", flow_id, limit=limit, sort=sort)


async def load_by_profile(profile_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> StorageRecords:
    return await storage_manager('console-log').load_by("profile_id", profile_id, limit=limit, sort=sort)


async def load_by_event(event_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> StorageRecords:
    return await storage_manager('console-log').load_by("event_id", event_id, limit=limit, sort=sort)


async def load_by_node(node_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> StorageRecords:
    return await storage_manager('console-log').load_by("node_id", node_id, limit=limit, sort=sort)


async def load_all() -> StorageRecords:
    return await storage_manager('console-log').load_all()


async def save_all(logs: list):
    return await storage_manager('console-log').upsert(logs)
