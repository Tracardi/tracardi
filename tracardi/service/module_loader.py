import inspect
import subprocess
import importlib
import importlib.util
from typing import Callable

import sys


def pip_install(package, upgrade=False):
    if upgrade:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-U'])
    else:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


def import_package(package):
    return importlib.import_module(package)


def load_callable(module, className) -> Callable:
    return getattr(module, className)


def is_installed(package_name):
    if package_name in sys.modules or importlib.util.find_spec(package_name) is not None:
        return True
    else:
        return False


def is_coroutine(object):
    return inspect.iscoroutinefunction(object)
