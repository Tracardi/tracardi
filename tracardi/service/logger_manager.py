from time import time

from typing import Optional

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver.elastic import log as log_db

error_collection = []
last_error_save = time()

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
        await log_db.save(log_handler.collection)
        last_error_save = time()
        log_handler.reset()
        return True

    return False
