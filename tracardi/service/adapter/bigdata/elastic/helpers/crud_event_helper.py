from tracardi.domain.event import Event
from tracardi.domain.flat_event import FlatEvent

from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.common.logging.log_handler import get_logger
from tracardi.service.storage.elastic.driver.factory import storage_manager
from typing import List, Optional, Union, Set

logger = get_logger(__name__)


async def load(id: str) -> Optional[StorageRecord]:
    return await storage_manager("event").load(id)


async def save(events: Union[List[FlatEvent], List[Event], Set[Event]], exclude=None):
    return await storage_manager("event").upsert(events, exclude=exclude)


async def delete_by_id(id: str) -> dict:
    sm = storage_manager("event")
    # Delete in all indices
    return await sm.delete(id, index=sm.get_multi_storage_alias())


async def search(query: dict):
    return await storage_manager("event").query({"query": query})


async def query(query: dict) -> StorageRecords:
    return await storage_manager("event").query(query)


def scan(query: dict = None, batch: int = 1000):
    return storage_manager('event').scan(query, batch)
