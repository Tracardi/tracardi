from typing import Optional

from contextlib import asynccontextmanager

from tracardi.cluster_config import is_save_logs_on
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import ElasticLogHandler


@asynccontextmanager
async def log_controller(log_handler: ElasticLogHandler) -> Optional[list]:
    if tracardi.save_logs and log_handler.has_logs():
        try:
            if await is_save_logs_on():
                yield log_handler.collection
        finally:
            log_handler.reset()
    else:
        yield None