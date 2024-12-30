from uuid import uuid4
from time import time
from tracardi.common.singleton import Singleton


class ApiInstance(metaclass=Singleton):
    def __init__(self):
        self.id = str(uuid4())
        self._start_time = time()

