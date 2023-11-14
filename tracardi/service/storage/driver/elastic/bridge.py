import logging
from typing import Optional

from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.bridge import Bridge
from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.factory import storage_manager

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def load_all(sort=None) -> StorageRecords:
    return await storage_manager('bridge').load_all(sort=sort)


async def load_by_id(id: str) -> Optional[StorageRecord]:
    return await storage_manager('bridge').load(id)


async def delete_by_id(id: str) -> dict:
    sm = storage_manager('bridge')
    return await sm.delete(id, index=sm.get_single_storage_index())


async def save(bridge: Bridge):
    return await storage_manager('bridge').upsert(bridge)


async def uninstall_bridge(bridge_id):
    if get_context().is_production():
        bridge_id = f"prod-{bridge_id}"
    else:
        bridge_id = f"stage-{bridge_id}"

    result = await delete_by_id(bridge_id)
    logger.info(f"Bridge unregistered with id {bridge_id} and result {result}")
    return result


async def install_bridge(bridge: Bridge):
    bridge_record = await load_by_id(bridge.id)

    if bridge_record is not None:
        if 'config' in bridge_record:
            bridge.config = bridge_record['config']

    # Depending on the type bridge Production or Staging add prefix
    if get_context().is_production():
        bridge.name = f"(Production) {bridge.name}"
        bridge.id = f"prod-{bridge.id}"
    else:
        bridge.name = f"(Test) {bridge.name}"
        bridge.id = f"stage-{bridge.id}"

    result = await save(bridge)
    logger.info(f"Bridge registered with id {bridge.id} and result {result}")
