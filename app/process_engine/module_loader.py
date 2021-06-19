import importlib


def load_callable(module, className):
    module = importlib.import_module(module)
    return getattr(module, className)

