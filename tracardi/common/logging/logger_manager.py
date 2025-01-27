from tracardi.context import get_context
from tracardi.common.logging.log_controller import log_controller
from tracardi.common.logging.log_handler import log_handler, get_installation_logger
from tracardi.service.dependency.adapters.big_data_adapter import bd_install_adapter

from tracardi.service.license import License

logger = get_installation_logger(__name__)
_bd_install_adapter = bd_install_adapter()

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
                if await _bd_install_adapter.has_logs_index(get_context()):
                    return await bd_log_adapter.save_logs(logs)
                else:
                    logger.warning(
                        "Logs index is not available. Probably system is not installed or being installed or the index went missing.")

