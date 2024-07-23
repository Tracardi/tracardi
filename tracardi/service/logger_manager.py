from tracardi.context import get_context
from tracardi.exceptions.log_handler import log_handler, get_installation_logger
from tracardi.service.cluster.config import is_save_logs_on
from tracardi.service.license import License
from tracardi.domain.installation_status import installation_status
from tracardi.service.storage.elastic.interface import log as log_db

logger = get_installation_logger(__name__)

if License.has_license():
    from com_tracardi.workers.log_saver import log_saver_worker


def logger_guard(logs):
    return bool(logs)


async def save_logs():
    if log_handler.has_logs():

        try:

            if not await is_save_logs_on():
                return None

            # Saving logs is on

            logs = log_handler.collection
            if License.has_license():
                # Runs only if there are logs (see logger_guard) and it is deferred.
                await log_saver_worker(logs)
            else:
                if await installation_status.has_logs_index(get_context()):
                    return await log_db.save(logs)
                else:
                    logger.warning(
                        "Logs index is not available. Probably system is not installed or being installed or the index went missing.")
        finally:
            log_handler.reset()
