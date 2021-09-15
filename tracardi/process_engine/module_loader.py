import subprocess
import importlib
import importlib.util
import sys


def pip_install(package, upgrade=False):
    if upgrade:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-U'])
    else:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


def import_and_install(package, upgrade=False):
    if upgrade:
        pip_install(package.split(".")[0], upgrade=True)

    try:
        return importlib.import_module(package)
    except ImportError:
        pip_install(package.split(".")[0])
    return importlib.import_module(package)


def load_callable(module, className, upgrade=False):
    module = import_and_install(module, upgrade)
    return getattr(module, className)


def is_installed(package_name):
    if package_name in sys.modules or importlib.util.find_spec(package_name) is not None:
        return True
    else:
        return False
