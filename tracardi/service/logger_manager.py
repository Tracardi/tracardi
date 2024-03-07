from com_tracardi.workers.example import deferred_execution
from com_tracardi.workers.log_saver import log_saver

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler

def logger_guard(logs):
    return bool(logs)

async def save_logs():

    if not tracardi.save_logs:
        return None

    if log_handler.has_logs():
        logs = log_handler.collection
        log_handler.reset()
        # Runs only if there are logs (see logger_guard) and it is deferred.
        with deferred_execution(guard=logger_guard) as defer:
            defer(log_saver)(logs).queue("Saving logs")
