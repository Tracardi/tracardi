from tracardi.context import get_context
from tracardi.common.logging.log_controller import log_controller
from tracardi.common.logging.log_handler import log_handler, get_installation_logger
from tracardi.service.adapter.bigdata.adapter_selector import bd_log_adapter
from tracardi.service.license import License
from tracardi.install.domain.installation_status import installation_status

logger = get_installation_logger(__name__)
_log_adapter = bd_log_adapter()

if License.has_license():
    from com_tracardi.workers.log_saver import log_saver_worker


def logger_guard(logs):
    return bool(logs)


async def save_logs():
    async with log_controller(log_handler) as logs:
        if logs:
            if License.has_license():
                # Runs only if there are logs (see logger_guard) and it is deferred.
                await log_saver_worker(logs)
            else:
                if await installation_status.has_logs_index(get_context()):
                    return await _log_adapter.save_logs(logs)
                else:
                    logger.warning(
                        "Logs index is not available. Probably system is not installed or being installed or the index went missing.")

