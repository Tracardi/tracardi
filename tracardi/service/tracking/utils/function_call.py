from dotty_dict import Dotty
from tracardi.service.module_loader import load_callable, import_package

def default_event_call_function(call_string, event: Dotty, profile: Dotty):
    state = call_string[5:]
    module, function = state.split(',')
    module = import_package(module)
    state_function = load_callable(module, function)

    return state_function(event, profile)