from typing import Optional, AsyncGenerator

from contextlib import asynccontextmanager

from tracardi.cluster_config import is_save_logs_on
from tracardi.config import tracardi
from tracardi.common.logging.log_handler import ElasticLogHandler


@asynccontextmanager
async def log_controller(log_handler: ElasticLogHandler) -> AsyncGenerator[Optional[list], None]:
    if tracardi.save_logs and log_handler.has_logs():
        try:
            # Check global settings
            if await is_save_logs_on():
                yield log_handler.collection
            else:
                yield None

        finally:
            log_handler.reset()
    else:
        yield None