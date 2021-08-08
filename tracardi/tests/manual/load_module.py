import importlib


def load(module, className):
    module = importlib.import_module(module)
    loaded_class = getattr(module, className)
    # return loaded_class(self)

load("importlib","y")