import logging

from dotty_dict import Dotty

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.module_loader import load_callable, import_package

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

def default_event_call_function(call_string, event: Dotty, profile: Dotty):
    state = call_string[5:]
    module, function = state.split(',')
    module = import_package(module)
    state_function = load_callable(module, function)
    try:
        return state_function(event, profile)
    except Exception as e:
        logger.error(str(e))
        return None