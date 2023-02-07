import asyncio
from typing import Optional

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver import storage


async def save_logs() -> Optional[bool]:
    if not tracardi.save_logs:
        return None
    """
    Saves errors caught by logger
    """
    if not await storage.driver.log.exists():
        return False

    if log_handler.has_logs():
        # do not await
        asyncio.create_task(storage.driver.log.save(log_handler.collection))
        log_handler.reset()
        return True

    return None
