import pip
import importlib


def import_and_install(package, upgrade=False):

    if upgrade:
        pip.main(['install', '--upgrade', package.split(".")[0]])

    try:
        return importlib.import_module(package)
    except ImportError:
        pip.main(['install', package.split(".")[0]])
    return importlib.import_module(package)


def load_callable(module, className, upgrade=False):
    module = import_and_install(module, upgrade)
    return getattr(module, className)
