from contextlib import contextmanager
from time import time


@contextmanager
def profiler():
    t1 = time()
    result = {}
    try:
        yield result
    finally:
        result["duration"] = time() - t1
