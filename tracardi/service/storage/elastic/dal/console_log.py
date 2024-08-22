from typing import List, Dict, Tuple

from tracardi.service.storage.elastic.driver.factory import storage_manager


async def load_by_flow(flow_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
    result = await storage_manager('log').load_by("flow_id", flow_id, limit=limit, sort=sort)
    return list(result), result.total


async def load_by_profile(profile_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
    result = await storage_manager('log').load_by("profile_id", profile_id, limit=limit, sort=sort)
    return list(result), result.total


async def load_by_event(event_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
    result = await storage_manager('log').load_by("event_id", event_id, limit=limit, sort=sort)
    return list(result), result.total


async def load_by_node(node_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
    result = await storage_manager('log').load_by("node_id", node_id, limit=limit, sort=sort)
    return list(result), result.total
