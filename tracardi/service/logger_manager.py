from tracardi.context import get_context
from tracardi.domain.installation_status import installation_status
from time import time
from typing import Optional

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler, get_installation_logger
from tracardi.service.storage.driver.elastic import log as log_db

error_collection = []
last_error_save = time()
logger = get_installation_logger(__name__)

async def save_logs() -> Optional[bool]:

    global error_collection, last_error_save

    if not tracardi.save_logs:
        return None

    # if log_handler.has_logs():
    #     error_collection += log_handler.collection
    #     last_error_save = time()
    #     log_handler.reset()
    #
    # if len(error_collection) > 500 or time() - last_error_save > 30:
    #     await log_db.save(error_collection)
    #     error_collection = []
    #     return True

    if log_handler.has_logs():
        try:
            if await installation_status.has_logs_index(get_context().tenant):
                await log_db.save(log_handler.collection)
            else:
                logger.warning("Logs index is not available. Probably system is not installed or being installed or the index went missing.")
        except Exception:
            logger.warning(f"Could not save log to elastic search.")
        last_error_save = time()
        log_handler.reset()
        return True

    return False
