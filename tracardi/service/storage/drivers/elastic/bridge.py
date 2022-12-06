import logging
from typing import Optional

from tracardi.config import tracardi
from tracardi.domain.bridge import Bridge
from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.service.storage.factory import storage_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)


async def load_all() -> StorageRecords:
    return await storage_manager('bridge').load_all()


async def load_by_id(id: str) -> Optional[StorageRecord]:
    return await storage_manager('bridge').load(id)


async def delete_by_id(id: str) -> dict:
    sm = storage_manager('bridge')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def save(bridge: Bridge):
    return await storage_manager('bridge').upsert(bridge)


async def install_bridge(bridge: Bridge):
    source = await load_by_id(bridge.id)
    if source is None:
        result = await save(bridge)
        logger.info(f"Bridge registered with id {bridge.id} and result {result}")