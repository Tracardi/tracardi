import os

_local_dir = os.path.dirname(__file__)


def read(file):
    with open(os.path.join(_local_dir, file)) as f:
        return f.read()
