import asyncio
from typing import Optional

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver.storage.driver import log as log_db


async def save_logs() -> Optional[bool]:
    if not tracardi.save_logs:
        return None
    """
    Saves errors caught by logger
    """
    if not await log_db.exists():
        return False

    if log_handler.has_logs():
        # do not await
        asyncio.create_task(log_db.save(log_handler.collection))
        log_handler.reset()
        return True

    return None
