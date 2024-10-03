from contextlib import contextmanager
from time import time


@contextmanager
def profiler(name):
    t1 = time()
    yield
    print(name, time() - t1)