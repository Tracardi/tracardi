from dotty_dict import Dotty

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.module_loader import load_callable, import_package

logger = get_logger(__name__)

def default_event_call_function(call_string, event: Dotty, profile: Dotty):
    state = call_string[5:]
    module, function = state.split(',')
    module = import_package(module)
    state_function = load_callable(module, function)
    try:
        if state_function is None:
            raise ValueError(f"Could not find function {function} in module {module}")

        return state_function(event, profile)

    except Exception as e:
        logger.error(str(e))
        return None