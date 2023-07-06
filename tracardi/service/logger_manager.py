from typing import Optional

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver.elastic import log as log_db


async def save_logs() -> Optional[bool]:
    if not tracardi.save_logs:
        return None

    # Will run one every 30s or 100 logs
    if log_handler.has_logs():
        # do not await
        await log_db.save(log_handler.collection)
        log_handler.reset()
        return True

    return False
